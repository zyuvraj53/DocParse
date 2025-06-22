import { Routes, Route, Link } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import ResumeParser from "./pages/ResumeParser";
import "./App.css";

export default function App() {
  return (
    <div className="App-layout">
      <Sidebar />
      <div className="Navbar-Viewport">
        <Navbar />
        <div className="Viewport">
          <Routes>
            <Route path="/" element={<MainContent />} />
            <Route path="/ResumeParser" element={<ResumeParser />} />
            {/* Add more routes as needed */}
          </Routes>
        </div>
      </div>
    </div>
  );
}

function MainContent() {
  return (
    <div className="Main-Content">
      <div className="Viewport-Section">
        <Link to="/ResumeParser" className="nav-link">
          Parse Resumes
        </Link>
      </div>
      <div className="Viewport-Section">
        Parse Joining Documents
        <div className="Viewport-Subsection">Educational Certificates</div>
        <div className="Viewport-Subsection">Experience Letters</div>
        <div className="Viewport-Subsection">Payslip Parsing</div>
      </div>
      <div className="Viewport-Section">
        Experience Reimbursement Parsing
        <div className="Viewport-Subsection">Invoice/Receipt Parsing</div>
        <div className="Viewport-Subsection">Category Mapping</div>
        <div className="Viewport-Subsection">Fraud & Duplication Detection</div>
        <div className="Viewport-Subsection">Policy Compliance Check</div>
      </div>
    </div>
  );
}
