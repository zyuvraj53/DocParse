import { useDropzone } from "react-dropzone";
import { useState } from "react";
import { Upload, Trash2 } from "lucide-react";

export default function EdCertParser() {
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState({ isLoading: false, type: null });
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processedCertificates, setProcessedCertificates] = useState([]);
  const [error, setError] = useState(null);

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

  const removeFile = (fileToRemove) => {
    setPendingFiles((prev) =>
      prev.filter(
        (file) =>
          !(file.name === fileToRemove.name && file.size === fileToRemove.size)
      )
    );
  };

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
      const response = await fetch("http://localhost:8000/certificates/upload-certificates", {
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

  const processCertificates = async () => {
    setLoadingStatus({ isLoading: true, type: "processing" });
    setError(null);

    try {
      const results = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const processResponse = await fetch("http://localhost:8000/certificates/process-certificates", {
          method: "POST",
          body: formData,
        });

        if (processResponse.ok) {
          const { certificate } = await processResponse.json();
          if (certificate) {
            results.push({
              ...certificate,
              authenticity_score: certificate.authenticity?.overall_score,
              has_digital_signature: certificate.authenticity?.digital_signatures?.has_digital_signature,
              document_hash: certificate.authenticity?.document_hash,
              certificate_endpoint_id: certificate.id
            });
          }
        } else {
          setError(`Processing failed for ${file.name}: ${processResponse.statusText}`);
          results.push({
            file_name: file.name,
            certificate_endpoint_id: "Failed",
          });
        }
      }

      setProcessedCertificates(results);
    } catch (error) {
      setError(`Error processing certificates: ${error.message}`);
    } finally {
      setLoadingStatus({ isLoading: false, type: null });
    }
  };

  const reset = () => {
    setPendingFiles([]);
    setUploadedFiles([]);
    setProcessedCertificates([]);
    setUploadSuccess(false);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop,
    multiple: true,
  });

  const displayValue = (value, fallback = "N/A") => {
    if (value === null || value === undefined || value === "") return fallback;
    return value;
  };

  const getScoreColor = (score) => {
    if (!score) return "#718096";
    if (score > 75) return "#48bb78";
    if (score > 50) return "#ed8936";
    return "#f56565";
  };

  return (
    <div style={{
      maxWidth: "1200px",
      margin: "0 auto",
      padding: "20px",
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>
      <h1 style={{
        fontSize: "28px",
        fontWeight: "600",
        color: "#2d3748",
        marginBottom: "24px",
        textAlign: "center"
      }}>Educational Certificate Parser</h1>
      
      <div {...getRootProps()} style={{
        border: "2px dashed #cbd5e0",
        borderRadius: "12px",
        padding: "40px",
        textAlign: "center",
        cursor: "pointer",
        backgroundColor: isDragActive ? "#f8fafc" : "#ffffff",
        transition: "background-color 0.2s ease",
        marginBottom: "24px"
      }}>
        <input {...getInputProps()} />
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "12px"
        }}>
          <Upload size={48} color="#4a5568" />
          <p style={{
            fontSize: "18px",
            color: "#4a5568",
            margin: 0
          }}>
            {isDragActive ? "Drop certificate PDFs here" : "Drag & drop certificate PDFs, or click to browse"}
          </p>
        </div>
      </div>

      {pendingFiles.length > 0 && (
        <div style={{ marginBottom: "24px" }}>
          <h3 style={{ fontSize: "18px", color: "#4a5568", marginBottom: "12px" }}>Files to upload:</h3>
          <ul style={{
            listStyle: "none",
            padding: 0,
            margin: 0,
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            overflow: "hidden"
          }}>
            {pendingFiles.map((file, index) => (
              <li key={index} style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "12px 16px",
                backgroundColor: index % 2 === 0 ? "#ffffff" : "#f8fafc",
                borderBottom: "1px solid #e2e8f0"
              }}>
                <span style={{
                  fontSize: "14px",
                  color: "#2d3748",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  flex: 1
                }}>{file.name}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(file);
                  }}
                  style={{
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: "pointer",
                    padding: "4px",
                    marginLeft: "12px",
                    color: "#e53e3e"
                  }}
                >
                  <Trash2 size={18} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: "#fff5f5",
          color: "#e53e3e",
          padding: "12px 16px",
          borderRadius: "8px",
          marginBottom: "24px",
          border: "1px solid #fed7d7"
        }}>
          {error}
        </div>
      )}

      <div style={{
        display: "flex",
        gap: "12px",
        marginBottom: "24px",
        flexWrap: "wrap"
      }}>
        <button
          onClick={uploadFiles}
          disabled={pendingFiles.length === 0 || loadingStatus.isLoading}
          style={{
            backgroundColor: pendingFiles.length > 0 && !loadingStatus.isLoading ? "#4299e1" : "#cbd5e0",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "6px",
            cursor: pendingFiles.length > 0 && !loadingStatus.isLoading ? "pointer" : "not-allowed",
            fontWeight: "600",
            fontSize: "14px",
            transition: "background-color 0.2s ease",
            minWidth: "150px"
          }}
        >
          {loadingStatus.isLoading && loadingStatus.type === "uploading" ? "Uploading..." : "Upload Files"}
        </button>
        
        <button
          onClick={processCertificates}
          disabled={!uploadSuccess || loadingStatus.isLoading}
          style={{
            backgroundColor: uploadSuccess && !loadingStatus.isLoading ? "#38a169" : "#cbd5e0",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "6px",
            cursor: uploadSuccess && !loadingStatus.isLoading ? "pointer" : "not-allowed",
            fontWeight: "600",
            fontSize: "14px",
            transition: "background-color 0.2s ease",
            minWidth: "150px"
          }}
        >
          {loadingStatus.isLoading && loadingStatus.type === "processing" ? "Processing..." : "Process Certificates"}
        </button>
        
        <button
          onClick={reset}
          style={{
            backgroundColor: "#e53e3e",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "14px",
            transition: "background-color 0.2s ease",
            minWidth: "150px"
          }}
        >
          Reset
        </button>
      </div>

      {processedCertificates.length > 0 && (
        <div>
          <h2 style={{
            fontSize: "20px",
            color: "#2d3748",
            marginBottom: "16px"
          }}>Processed Certificates</h2>
          
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "20px"
          }}>
            {processedCertificates.map((cert) => (
              <div key={cert.id || cert.certificate_endpoint_id} style={{
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                padding: "16px",
                backgroundColor: "#ffffff",
                boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
                transition: "transform 0.2s ease"
              }}>
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "12px",
                  paddingBottom: "8px",
                  borderBottom: "1px solid #edf2f7"
                }}>
                  <h3 style={{
                    margin: 0,
                    fontSize: "16px",
                    color: "#2d3748",
                    fontWeight: "600"
                  }}>{displayValue(cert.university)}</h3>
                  
                  {cert.authenticity_score && (
                    <span style={{
                      backgroundColor: getScoreColor(cert.authenticity_score),
                      color: "white",
                      padding: "4px 8px",
                      borderRadius: "12px",
                      fontSize: "12px",
                      fontWeight: "bold"
                    }}>
                      {cert.authenticity_score.toFixed(1)}/100
                    </span>
                  )}
                </div>
                
                <div style={{ marginBottom: "12px" }}>
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>Degree:</span>
                    <span>{displayValue(cert.degree)}</span>
                  </div>
                  
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>Graduation:</span>
                    <span>{displayValue(cert.graduation_date)}</span>
                  </div>
                  
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>GPA:</span>
                    <span>{displayValue(cert.gpa)}</span>
                  </div>
                </div>
                
                <div style={{
                  paddingTop: "8px",
                  borderTop: "1px solid #edf2f7",
                  marginTop: "8px"
                }}>
                  <h4 style={{
                    fontSize: "14px",
                    color: "#4a5568",
                    margin: "0 0 8px 0",
                    fontWeight: "600"
                  }}>Authenticity Details</h4>
                  
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>Document Hash:</span>
                    <span style={{
                      fontFamily: "monospace",
                      fontSize: "12px",
                      color: "#718096",
                      wordBreak: "break-all",
                      textAlign: "right",
                      maxWidth: "60%"
                    }}>
                      {cert.document_hash ? `${cert.document_hash.substring(0, 12)}...` : 'N/A'}
                    </span>
                  </div>
                  
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>Digital Signature:</span>
                    <span>
                      {cert.has_digital_signature === "true" ? "✅ Verified" : "❌ Not Verified"}
                    </span>
                  </div>
                  
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#718096", fontWeight: "500" }}>File:</span>
                    <span style={{
                      fontFamily: "monospace",
                      fontSize: "12px",
                      color: "#4a5568",
                      wordBreak: "break-all",
                      textAlign: "right",
                      maxWidth: "60%"
                    }}>
                      {displayValue(cert.source_file)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}