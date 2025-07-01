import { useDropzone } from "react-dropzone";
import { useState, useEffect } from "react";
import { Upload, Trash2 } from "lucide-react";
import { Radar, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import "./index.css";

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

export default function ResumeParser() {
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState({ isLoading: false, type: null });
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processedResumes, setProcessedResumes] = useState([]);
  const [error, setError] = useState(null);
  const [topPdfsCount, setTopPdfsCount] = useState(0);
  const [candidateCount, setCandidateCount] = useState(1); // New state for dropdown
  const [candidateDetails, setCandidateDetails] = useState([]); // Store /resumes/{id} data

  // Utility function to format dates to ISO
  const toISODateString = (dateString) => {
    try {
      return new Date(dateString).toISOString();
    } catch {
      return new Date().toISOString();
    }
  };

  // Fetch candidate details from /resumes/{id}
  useEffect(() => {
    const fetchCandidateDetails = async () => {
      if (sortedFitScores.length === 0) return;

      const selectedCandidates = sortedFitScores.slice(0, candidateCount);
      const details = [];

      for (const candidate of selectedCandidates) {
        if (candidate.id && candidate.id !== "Unknown" && candidate.id !== "Failed" && candidate.id !== "Error") {
          try {
            const response = await fetch(`http://localhost:8000/resumes/${candidate.id}`);
            if (response.ok) {
              const data = await response.json();
              details.push({ ...data, total_fit_score: candidate.total_fit_score });
            } else {
              console.warn(`Failed to fetch resume ${candidate.id}: ${response.statusText}`);
            }
          } catch (err) {
            console.error(`Error fetching resume ${candidate.id}:`, err);
          }
        }
      }

      setCandidateDetails(details);
    };

    fetchCandidateDetails();
  }, [candidateCount, processedResumes]);

  // Handle file drop/selection
  const onDrop = (acceptedFiles) => {
    setError(null);
    const newFiles = acceptedFiles.filter(
      (newFile) =>
        !pendingFiles.some(
          (existingFile) =>
            existingFile.name === newFile.name &&
            existingFile.size === newFile.size
        )
    );
    setPendingFiles((prev) => [...prev, ...newFiles]);
  };

  // Remove a specific file
  const removeFile = (fileToRemove) => {
    setPendingFiles((prev) =>
      prev.filter(
        (file) =>
          !(file.name === fileToRemove.name && file.size === fileToRemove.size)
      )
    );
  };

  // Upload files
  const uploadFiles = async () => {
    if (pendingFiles.length === 0) {
      setError("No files to upload.");
      return;
    }

    setLoadingStatus({ isLoading: true, type: "uploading" });
    setUploadSuccess(false);
    setError(null);

    const formData = new FormData();
    pendingFiles.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch("http://localhost:8000/uploads/upload-resumes", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadSuccess(true);
        setUploadedFiles(pendingFiles);
        setPendingFiles([]);
      } else {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
    } catch (error) {
      setError(`Error uploading files: ${error.message}`);
    } finally {
      setLoadingStatus({ isLoading: false, type: null });
    }
  };

  // Process resumes and post to /resumes/
  const processResumes = async () => {
    setLoadingStatus({ isLoading: true, type: "processing" });
    setError(null);

    try {
      const results = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const processResponse = await fetch("http://localhost:8000/uploads/process-resumes", {
          method: "POST",
          body: formData,
        });

        if (processResponse.ok) {
          const processResult = await processResponse.json();
          const validResumes = processResult.resumes.filter((resume) => !resume.error);

          for (const resume of validResumes) {
            const resumePayload = {
              file_name: resume.filename,
              personal_information: {
                name: resume.entities.personal_info.name || "",
                email: resume.entities.personal_info.email || "",
                phone: resume.entities.personal_info.phone || "",
                location: resume.entities.personal_info.location || "",
              },
              education: resume.entities.education.map((edu) => ({
                institution: edu.institution || "",
                degree: edu.degree || "",
                field: edu.field || "",
              })),
              skills: {
                technical: [...new Set(resume.entities.skills.technical || [])],
                soft: [...new Set(resume.entities.skills.soft || [])],
              },
              languages: (resume.entities.languages || []).map((lang) => ({
                name: lang,
              })),
              tools: [...new Set(resume.entities.skills.technical || [])],
              concepts: [...new Set(resume.entities.skills.technical || [])],
              others: [],
              resume_metadata: {
                extracted_at: toISODateString(resume.processed_at),
                anonymized: !!resume.anonymized,
              },
            };

            try {
              const resumeResponse = await fetch("http://localhost:8000/resumes/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify(resumePayload),
              });

              if (resumeResponse.ok) {
                const resumeResponseData = await resumeResponse.json();
                results.push({
                  ...resume,
                  resume_endpoint_id: resumeResponseData.id || "Unknown",
                });
              } else {
                console.warn(`Failed to post resume ${resume.filename} to /resumes/: ${resumeResponse.statusText}`);
                setError((prev) => prev ? `${prev}\nFailed to save resume ${resume.filename}` : `Failed to save resume ${resume.filename}`);
                results.push({
                  ...resume,
                  resume_endpoint_id: "Failed",
                });
              }
            } catch (err) {
              console.error(`Error posting resume ${resume.filename}:`, err);
              setError((prev) => prev ? `${prev}\nError saving resume ${resume.filename}` : `Error saving resume ${resume.filename}`);
              results.push({
                ...resume,
                resume_endpoint_id: "Error",
              });
            }
          }
        } else {
          setError(`Processing failed for ${file.name}: ${processResponse.statusText}`);
        }
      }

      setProcessedResumes(results);
    } catch (error) {
      setError(`Error processing resumes: ${error.message}`);
    } finally {
      setLoadingStatus({ isLoading: false, type: null });
    }
  };

  // Reset state
  const reset = () => {
    setPendingFiles([]);
    setUploadedFiles([]);
    setProcessedResumes([]);
    setUploadSuccess(false);
    setError(null);
    setTopPdfsCount(0);
    setCandidateCount(1);
    setCandidateDetails([]);
  };

  // Handle top PDFs selection
  const handleTopPdfsChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 0 && value <= processedResumes.length) {
      setTopPdfsCount(value);
    }
  };

  // Handle candidate count selection
  const handleCandidateCountChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= processedResumes.length) {
      setCandidateCount(value);
    }
  };

  // Create and sort list of (total_fit_score, resume_endpoint_id)
  const sortedFitScores = processedResumes
    .map((resume) => ({
      total_fit_score: resume.fit_scores?.total_fit || 0,
      id: resume.resume_endpoint_id || "Unknown",
    }))
    .sort((a, b) => b.total_fit_score - a.total_fit_score);

  // Prepare data for spider chart
  const spiderChartData = {
    labels: ["Technical Skills", "Soft Skills", "Languages", "Tools"],
    datasets: candidateDetails.map((candidate, index) => ({
      label: candidate.personal_information?.name || `Candidate ${index + 1}`,
      data: [
        Math.min((candidate.skills?.technical?.length || 0) / 5, 10), // Normalize to 0-10
        Math.min((candidate.skills?.soft?.length || 0) / 5, 10),
        Math.min((candidate.languages?.length || 0) / 5, 10),
        Math.min((candidate.tools?.length || 0) / 5, 10),
      ],
      backgroundColor: `rgba(${75 + index * 50}, ${192 - index * 50}, ${192}, 0.2)`,
      borderColor: `rgba(${75 + index * 50}, ${192 - index * 50}, ${192}, 1)`,
      borderWidth: 1,
    })),
  };

  // Prepare data for bar chart
  const barChartData = {
    labels: candidateDetails.map((c) => c.personal_information?.name || `Candidate ${c.id}`),
    datasets: [
      {
        label: "Technical Skills",
        data: candidateDetails.map((c) => c.skills?.technical?.length || 0),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
      {
        label: "Soft Skills",
        data: candidateDetails.map((c) => c.skills?.soft?.length || 0),
        backgroundColor: "rgba(255, 99, 132, 0.6)",
      },
      {
        label: "Languages",
        data: candidateDetails.map((c) => c.languages?.length || 0),
        backgroundColor: "rgba(54, 162, 235, 0.6)",
      },
      {
        label: "Tools",
        data: candidateDetails.map((c) => c.tools?.length || 0),
        backgroundColor: "rgba(255, 206, 86, 0.6)",
      },
    ],
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop,
    multiple: true,
  });

  return (
    <div className="Layout">
      <div className="space-grotesk Subtitle">Resume Parser</div>
      <div>
        {/* Dropzone */}
        <div
          {...getRootProps()}
          style={{
            border: "2px dashed #1a202c",
            borderRadius: "1vw",
            padding: "2vw",
            margin: "2vw",
            textAlign: "center",
            cursor: "pointer",
            minHeight: "25vh",
            alignContent: "center",
            backgroundColor: isDragActive ? "#f0f0f0" : "white",
          }}
        >
          <input {...getInputProps()} multiple />
          {isDragActive ? (
            <div>Drop the PDFs here...</div>
          ) : (
            <div>
              <span>
                <Upload />
              </span>
              <span style={{ paddingLeft: "2vw" }}>
                Upload PDFs (Drag & drop or click)
              </span>
            </div>
          )}
        </div>

        {/* Pending Files List */}
        {pendingFiles.length > 0 && (
          <div>
            <p>Staged {pendingFiles.length} file(s) for upload:</p>
            <ul>
              {pendingFiles.map((file, index) => (
                <li key={`${file.name}-${index}`}>
                  {file.name}{" "}
                  <button
                    onClick={() => removeFile(file)}
                    style={{
                      backgroundColor: "#dc3545",
                      color: "white",
                      border: "none",
                      padding: "2px 8px",
                      marginLeft: "10px",
                      cursor: "pointer",
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={{ color: "red", textAlign: "center", margin: "1vw" }}>
            {error}
          </div>
        )}

        {/* Upload, Process, and Reset Buttons */}
        <div style={{ textAlign: "center" }}>
          <button
            onClick={uploadFiles}
            disabled={pendingFiles.length === 0 || loadingStatus.isLoading}
            style={{
              backgroundColor:
                pendingFiles.length > 0 && !loadingStatus.isLoading
                  ? "#28a745"
                  : "#ccc",
              color: "white",
              padding: "10px 20px",
              border: "none",
              cursor:
                pendingFiles.length > 0 && !loadingStatus.isLoading
                  ? "pointer"
                  : "not-allowed",
              marginRight: "10px",
            }}
          >
            {loadingStatus.isLoading && loadingStatus.type === "uploading"
              ? "Uploading..."
              : "Upload Files"}
          </button>
          <button
            onClick={processResumes}
            disabled={!uploadSuccess || loadingStatus.isLoading}
            style={{
              backgroundColor:
                uploadSuccess && !loadingStatus.isLoading ? "#007bff" : "#ccc",
              color: "white",
              padding: "10px 20px",
              border: "none",
              cursor:
                uploadSuccess && !loadingStatus.isLoading
                  ? "pointer"
                  : "not-allowed",
              marginRight: "10px",
            }}
          >
            {loadingStatus.isLoading && loadingStatus.type === "processing"
              ? "Processing..."
              : "Process PDFs"}
          </button>
          <button
            onClick={reset}
            style={{
              backgroundColor: "#dc3545",
              color: "white",
              padding: "10px 20px",
              border: "none",
              cursor: "pointer",
            }}
          >
            Reset
          </button>
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div>
            <p>Uploaded {uploadedFiles.length} file(s):</p>
            <ul>
              {uploadedFiles.map((file, index) => (
                <li key={`${file.name}-${index}`}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Candidate Count Dropdown */}
        {processedResumes.length > 0 && (
          <div style={{ margin: "1vw", textAlign: "center" }}>
            <label>
              Select number of candidates to display (Max: {processedResumes.length}):
              <select
                value={candidateCount}
                onChange={handleCandidateCountChange}
                style={{ marginLeft: "10px", padding: "5px" }}
              >
                {[...Array(processedResumes.length).keys()].map((i) => (
                  <option key={i + 1} value={i + 1}>
                    {i + 1}
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}

        {/* Sorted Fit Scores List */}
        {/* {sortedFitScores.length > 0 && (
          <div>
            <p>Sorted Resumes by Total Fit Score:</p>
            <ul>
              {sortedFitScores
                .slice(0, topPdfsCount || sortedFitScores.length)
                .map((item, index) => (
                  <li key={item.id}>
                    ID: {item.id} - Total Fit Score: {item.total_fit_score.toFixed(2)}
                  </li>
                ))}
            </ul>
          </div>
        )} */}

        {/* Visualizations */}
        {candidateDetails.length > 0 && (
          <div style={{ margin: "2vw" }}>
            {/* Spider Chart */}
            <div style={{ marginBottom: "2vw", maxWidth: "600px", margin: "auto" }}>
              <h3>Skills Comparison (Spider Chart)</h3>
              <Radar
                data={spiderChartData}
                options={{
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 10,
                      ticks: { stepSize: 2 },
                    },
                  },
                  plugins: {
                    legend: { position: "top" },
                    title: { display: true, text: "Candidate Skills Profile" },
                  },
                }}
              />
            </div>

            {/* Bar Chart */}
            <div style={{ marginBottom: "2vw", maxWidth: "600px", margin: "auto" }}>
              <h3>Skills Count Comparison (Bar Chart)</h3>
              <Bar
                data={barChartData}
                options={{
                  scales: {
                    y: { beginAtZero: true, title: { display: true, text: "Count" } },
                    x: { title: { display: true, text: "Candidates" } },
                  },
                  plugins: {
                    legend: { position: "top" },
                    title: { display: true, text: "Candidate Skills Breakdown" },
                  },
                }}
              />
            </div>

            {/* Candidate Details Table */}
            <div style={{ marginBottom: "2vw" }}>
              <h3>Candidate Details</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f4f4f4" }}>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Name</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Fit Score</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Technical Skills</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Soft Skills</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Languages</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Tools</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px" }}>Education</th>
                  </tr>
                </thead>
                <tbody>
                  {candidateDetails.map((candidate) => (
                    <tr key={candidate.id}>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.personal_information?.name || "N/A"}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.total_fit_score.toFixed(2)}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.skills?.technical?.join(", ") || "None"}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.skills?.soft?.join(", ") || "None"}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.languages?.map((l) => l.name).join(", ") || "None"}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.tools?.join(", ") || "None"}
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {candidate.education
                          ?.map((e) => `${e.institution} (${e.degree || "N/A"}, ${e.field || "N/A"})`)
                          .join("; ") || "None"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Processed Resumes List */}
        {/* {processedResumes.length > 0 && (
          <div>
            <p>Processed {processedResumes.length} resume(s):</p>
            <ul>
              {processedResumes
                .slice(0, topPdfsCount || processedResumes.length)
                .map((resume, index) => (
                  <li key={resume.resume_endpoint_id || index}>
                    {resume.file_name || resume.filename} - Skills:{" "}
                    {resume.skills &&
                    (resume.skills.technical?.length || resume.skills.soft?.length)
                      ? [
                          ...(resume.skills.technical || []),
                          ...(resume.skills.soft || []),
                        ].join(", ") || "None"
                      : "None"} - Endpoint ID: {resume.resume_endpoint_id}
                  </li>
                ))}
            </ul> */}

            {/* Raw Response Data */}
            {/* <div>
              <h3>Raw Response Data</h3>
              {processedResumes
                .slice(0, topPdfsCount || processedResumes.length)
                .map((resume, index) => (
                  <div key={resume.resume_endpoint_id || index} style={{ marginBottom: "20px" }}>
                    <h4>
                      Resume {index + 1}: {resume.file_name || resume.filename} (Endpoint ID: {resume.resume_endpoint_id})
                    </h4>
                    <pre
                      style={{
                        background: "#f4f4f4",
                        padding: "10px",
                        overflowX: "auto",
                      }}
                    >
                      {JSON.stringify(resume, null, 2)}
                    </pre>
                  </div>
                ))}
            </div> */}

            {/* Top PDFs Selection */}
            {/* <div>
              <label>
                Choose how many top PDFs to display{" "}
                {processedResumes.length > 0 &&
                  `(Max: ${processedResumes.length})`}
                :
                <input
                  type="number"
                  min="0"
                  max={processedResumes.length}
                  value={topPdfsCount}
                  onChange={handleTopPdfsChange}
                  style={{ marginLeft: "10px", width: "60px" }}
                />
              </label>
            </div> */}
          {/* </div> */}
        {/* )} */}
      </div>
    </div>
  );
}