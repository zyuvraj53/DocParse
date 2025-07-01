import { useDropzone } from "react-dropzone";
import { useState } from "react";
import { Upload, Trash2 } from "lucide-react";
import "./index.css"; // Reuse the same CSS as ResumeParser for consistent styling

export default function PayslipParser() {
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState({ isLoading: false, type: null });
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processedPayslips, setProcessedPayslips] = useState([]);
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

  // Upload files to /uploads/upload-payslips
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
      const response = await fetch("http://localhost:8000/uploads/upload-payslips", {
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

  // Process payslips and post to /payslips/
  const processPayslips = async () => {
    setLoadingStatus({ isLoading: true, type: "processing" });
    setError(null);

    try {
      const results = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const processResponse = await fetch("http://localhost:8000/uploads/process-payslips", {
          method: "POST",
          body: formData,
        });

        if (processResponse.ok) {
          const processResult = await processResponse.json();
          const validPayslips = processResult.payslip ? [processResult.payslip] : [];

          for (const payslip of validPayslips) {
            results.push({
              ...payslip,
              payslip_endpoint_id: payslip.id || "Unknown",
            });
          }
        } else {
          setError(`Processing failed for ${file.name}: ${processResponse.statusText}`);
          results.push({
            file_name: file.name,
            payslip_endpoint_id: "Failed",
          });
        }
      }

      setProcessedPayslips(results);
    } catch (error) {
      setError(`Error processing payslips: ${error.message}`);
    } finally {
      setLoadingStatus({ isLoading: false, type: null });
    }
  };

  // Reset state
  const reset = () => {
    setPendingFiles([]);
    setUploadedFiles([]);
    setProcessedPayslips([]);
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
      <div className="space-grotesk Subtitle">Payslip Parser</div>
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
                Upload Payslip PDFs (Drag & drop or click)
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
            onClick={processPayslips}
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
              : "Process Payslips"}
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

        {/* Processed Payslips List */}
        {processedPayslips.length > 0 && (
          <div style={{ margin: "2vw" }}>
            <h3>Processed Payslips</h3>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr style={{ backgroundColor: "#f4f4f4" }}>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>File Name</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Employee Name</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Designation</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Valid</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Net Pay</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Payslip ID</th>
                </tr>
              </thead>
              <tbody>
                {processedPayslips.map((payslip) => (
                  <tr key={payslip.payslip_endpoint_id}>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.file_processed || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.employment_proof?.employee_name || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.employment_proof?.designation || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.employment_proof?.valid || "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.components?.net_pay ? `$${payslip.components.net_pay.toFixed(2)}` : "N/A"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      {payslip.payslip_endpoint_id}
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