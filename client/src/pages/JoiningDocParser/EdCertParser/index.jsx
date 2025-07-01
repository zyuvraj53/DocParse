import { useDropzone } from "react-dropzone";
import { useState, useEffect } from "react";
import { Upload, Trash2 } from "lucide-react";
import "./index.css";

export default function EdCertParser() {
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState({ isLoading: false, type: null });
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processedCertificates, setProcessedCertificates] = useState([]);
  const [error, setError] = useState(null);
  const [uploadButtonEnabled, setUploadButtonEnabled] = useState(false);
  const [processButtonEnabled, setProcessButtonEnabled] = useState(false);

  // Sample certificate data to simulate backend processing
  const sampleCertificates = [
    {
      certificate_type: "course_completion",
      issuing_organization: "University of Colorado Boulder",
      platform: "Coursera",
      recipient_name: "PRATYUSH KUMAR NAYAK",
      course_title: "Ethical Decision Making for Success in the Tech Industry",
      completion_date: "Mar 12, 2025",
      course_type: "online non-credit course",
      instructor: "Daniel Moorer",
      instructor_title: "Professor and Scholar in Residence, Lockheed Martin Engineering Management Program",
      verification_url: "https://coursera.org/verify/561.23KWFMC9P",
      identity_verified: true,
      authorizing_organization: "University of Colorado Boulder",
      certificate_id: "561.23KWFMC9P",
      file_name: "certificate.pdf"
    },
    {
      certificate_type: "course_completion",
      issuing_organization: "Meta",
      platform: "Coursera",
      recipient_name: "Piyush Prasun",
      course_title: "Introduction to Back-End Development",
      completion_date: "Jun 27, 2025",
      course_type: "online non-credit course",
      instructor: null,
      instructor_title: null,
      verification_url: "https://coursera.org/verify/E9JTEJR2R9TN",
      identity_verified: true,
      authorizing_organization: "Meta",
      certificate_id: "E9JTEJR2R9TN",
      file_name: "Coursera E9JTEJR2R9TN.pdf"
    }
  ];

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
    setUploadButtonEnabled(true);
  };

  // Remove a specific file
  const removeFile = (fileToRemove) => {
    setPendingFiles((prev) =>
      prev.filter(
        (file) =>
          !(file.name === fileToRemove.name && file.size === fileToRemove.size)
      )
    );
    if (pendingFiles.length <= 1) {
      setUploadButtonEnabled(false);
    }
  };

  // Simulate file upload with 2-second delay
  const uploadFiles = async () => {
    setLoadingStatus({ isLoading: true, type: "uploading" });
    setUploadSuccess(false);
    setError(null);

    await new Promise(resolve => setTimeout(resolve, 2000));

    setUploadSuccess(true);
    setUploadedFiles(pendingFiles);
    setPendingFiles([]);
    setLoadingStatus({ isLoading: false, type: null });
    setProcessButtonEnabled(true);
  };

  // Simulate processing with 2-second delay
  const processCertificates = async () => {
    setLoadingStatus({ isLoading: true, type: "processing" });
    setError(null);

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Match uploaded files with sample certificates by filename
    const results = uploadedFiles.map(file => {
      const matchedCert = sampleCertificates.find(cert => cert.file_name === file.name);
      return matchedCert || {
        file_name: file.name,
        certificate_endpoint_id: "No matching certificate data",
        error: "Certificate format not recognized"
      };
    });

    setProcessedCertificates(results);
    setLoadingStatus({ isLoading: false, type: null });
  };

  // Reset state
  const reset = () => {
    setPendingFiles([]);
    setUploadedFiles([]);
    setProcessedCertificates([]);
    setUploadSuccess(false);
    setError(null);
    setUploadButtonEnabled(false);
    setProcessButtonEnabled(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop,
    multiple: true,
  });

  return (
    <div className="Layout">
      <div className="space-grotesk Subtitle">Educational Certificate Parser</div>
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
                Upload Certificate PDFs (Drag & drop or click)
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
            disabled={!uploadButtonEnabled || loadingStatus.isLoading}
            style={{
              backgroundColor:
                uploadButtonEnabled && !loadingStatus.isLoading
                  ? "#28a745"
                  : "#ccc",
              color: "white",
              padding: "10px 20px",
              border: "none",
              cursor:
                uploadButtonEnabled && !loadingStatus.isLoading
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
            onClick={processCertificates}
            disabled={!processButtonEnabled || loadingStatus.isLoading}
            style={{
              backgroundColor:
                processButtonEnabled && !loadingStatus.isLoading ? "#007bff" : "#ccc",
              color: "white",
              padding: "10px 20px",
              border: "none",
              cursor:
                processButtonEnabled && !loadingStatus.isLoading
                  ? "pointer"
                  : "not-allowed",
              marginRight: "10px",
            }}
          >
            {loadingStatus.isLoading && loadingStatus.type === "processing"
              ? "Processing..."
              : "Process Certificates"}
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

        {/* Processed Certificates List */}
        {processedCertificates.length > 0 && (
          <div style={{ margin: "2vw" }}>
            <h3>Processed Certificates</h3>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr style={{ backgroundColor: "#f4f4f4" }}>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Recipient</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Course</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Issuing Org</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Completion Date</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Instructor</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Verification URL</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>File Name</th>
                </tr>
              </thead>
              <tbody>
                {processedCertificates.map((cert, index) => (
                  <tr key={index}>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.recipient_name || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.course_title || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.issuing_organization || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.completion_date || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.instructor || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.verification_url ? (
                        <a href={cert.verification_url} target="_blank" rel="noopener noreferrer">
                          Verify
                        </a>
                      ) : "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {cert.file_name || "N/A"}
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