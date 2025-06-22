import "./index.css";

export default function ResumeParser() {
  return (
    <div className="Layout">
      <div className="space-grotesk Subtitle">Resume Parser</div>
      <div>
        <div>Upload pdfs</div> {/* Button */}
        <div>
          process pdfs{" "}
          {/* Should be a button, should only be clickable when
          uploading is done successfully */}
        </div>
      </div>
      <div>
        Content about the uploaded pdfs
        <div>
          Choose how many top pdfs you want to see{" "}
          {/* Should not exceed the number of pdfs uploaded */}
        </div>
      </div>
    </div>
  );
}
