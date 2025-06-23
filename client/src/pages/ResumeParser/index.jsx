import { useDropzone } from 'react-dropzone';
import { useState } from 'react';
import "./index.css";

export default function ResumeParser() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedResumes, setProcessedResumes] = useState([]);

  const uploadFiles = async (files) => {
    setIsUploading(true);
    setUploadSuccess(false);
    
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/uploads/upload-resumes', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Upload successful:', result);
        setUploadSuccess(true);
        setUploadedFiles(files);
      } else {
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const processResumes = async () => {
    setIsProcessing(true);
    
    try {
      const results = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('http://localhost:8000/uploads/process-resumes', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          results.push(...result.resumes.filter(resume => !resume.error));
        } else {
          console.error('Processing failed for', file.name, ':', response.statusText);
        }
      }
      
      console.log('Processing successful:', results);
      setProcessedResumes(results);
    } catch (error) {
      console.error('Error processing resumes:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf']
    },
    onDrop: (acceptedFiles) => {
      uploadFiles(acceptedFiles);
    }
  });

  return (
    <div className="Layout">
      <div className="space-grotesk Subtitle">Resume Parser</div>
      <div>
        <div {...getRootProps()} style={{ 
          border: '2px dashed #ccc', 
          padding: '20px', 
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? '#f0f0f0' : 'white'
        }}>
          <input {...getInputProps()} />
          {isUploading ? (
            <div>Uploading files...</div>
          ) : isDragActive ? (
            <div>Drop the PDFs here ...</div>
          ) : (
            <div>Upload pdfs (Drag & drop or click)</div>
          )}
        </div>
        <div>
          <button 
            onClick={processResumes}
            disabled={!uploadSuccess || isProcessing}
            style={{
              backgroundColor: (uploadSuccess && !isProcessing) ? '#007bff' : '#ccc',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              cursor: (uploadSuccess && !isProcessing) ? 'pointer' : 'not-allowed'
            }}
          >
            {isProcessing ? 'Processing...' : 'Process PDFs'}
          </button>
        </div>
      </div>
      <div>
        Content about the uploaded pdfs
        {uploadedFiles.length > 0 && (
          <div>
            <p>Uploaded {uploadedFiles.length} file(s):</p>
            <ul>
              {uploadedFiles.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}
        
        {processedResumes.length > 0 && (
          <div>
            <p>Processed {processedResumes.length} resume(s):</p>
            <ul>
              {processedResumes.map((resume, index) => (
                <li key={resume.id || index}>
                  {resume.file_name || resume.filename} - Skills: {resume.skills && (resume.skills.technical || resume.skills.soft) 
                    ? [...(resume.skills.technical || []), ...(resume.skills.soft || [])].join(', ') 
                    : 'None'}
                </li>
              ))}
            </ul>
            <div>
              <h3>Raw Response Data</h3>
              {processedResumes.map((resume, index) => (
                <div key={resume.id || index} style={{ marginBottom: '20px' }}>
                  <h4>Resume {index + 1}: {resume.file_name || resume.filename}</h4>
                  <pre style={{ background: '#f4f4f4', padding: '10px', overflowX: 'auto' }}>
                    {JSON.stringify(resume, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div>
          Choose how many top pdfs you want to see{" "}
          {processedResumes.length > 0 && `(Max: ${processedResumes.length})`}
        </div>
      </div>
    </div>
  );
}