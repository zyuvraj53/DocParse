import { useDropzone } from "react-dropzone";
import { useState } from "react";
import { Upload, Trash2 } from "lucide-react";
import "./index.css";

export default function ExperienceLetterParser() {
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState({ isLoading: false, type: null });
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processedLetters, setProcessedLetters] = useState([]);
  const [error, setError] = useState(null);

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

  // Upload files to /uploads/upload-experience-letters
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
      const response = await fetch("http://localhost:8000/uploads/upload-experience-letters", {
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

  // Process experience letters and post to /experience-letters/
  const processExperienceLetters = async () => {
    setLoadingStatus({ isLoading: true, type: "processing" });
    setError(null);

    try {
      const results = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const processResponse = await fetch("http://localhost:8000/uploads/process-experience-letters", {
          method: "POST",
          body: formData,
        });

        if (processResponse.ok) {
          const processResult = await processResponse.json();
          const validLetters = processResult.experience_letter ? [processResult.experience_letter] : [];

          for (const letter of validLetters) {
            results.push({
              ...letter,
              letter_endpoint_id: letter.id || "Unknown",
            });
          }
        } else {
          setError(`Processing failed for ${file.name}: ${processResponse.statusText}`);
          results.push({
            file_name: file.name,
            letter_endpoint_id: "Failed",
          });
        }
      }

      setProcessedLetters(results);
    } catch (error) {
      setError(`Error processing experience letters: ${error.message}`);
    } finally {
      setLoadingStatus({ isLoading: false, type: null });
    }
  };

  // Reset state
  const reset = () => {
    setPendingFiles([]);
    setUploadedFiles([]);
    setProcessedLetters([]);
    setUploadSuccess(false);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop,
    multiple: true,
  });

  return (
    <div className="Layout">
      <div className="space-grotesk Subtitle">Experience Letter Parser</div>
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
                Upload Experience Letter PDFs (Drag & drop or click)
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
            onClick={processExperienceLetters}
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
              : "Process Letters"}
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

        {/* Processed Experience Letters List */}
        {processedLetters.length > 0 && (
          <div style={{ margin: "2vw" }}>
            <h3>Processed Experience Letters</h3>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr style={{ backgroundColor: "#f4f4f4" }}>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>File Name</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Employee</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Organization</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Job Title</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Start Date</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>End Date</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Duration</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Confidence</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Anomalies</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Letter ID</th>
                </tr>
              </thead>
              <tbody>
                {processedLetters.map((letter) => (
                  <tr key={letter.letter_endpoint_id}>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.file_processed || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.employee_name || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.org_name || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.job_title || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.start_date || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.end_date || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.extracted_data?.duration_years ? `${letter.extracted_data.duration_years} years` : "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.confidence_score ? `${letter.confidence_score}%` : "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.anomalies?.length || 0}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {letter.letter_endpoint_id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}