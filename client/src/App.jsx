import { Routes, Route, Link } from 'react-router-dom';
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import ResumeParser from "./pages/ResumeParser";
import "./App.css";

export default function App() {
  return (
    <div className="App-layout">
      <Navbar />
      <div className="Sidebar-Viewport">
        <Sidebar />
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
    <>
      <div>
        <Link to="/ResumeParser" className="nav-link">Parse Resumes</Link>
      </div>
      <div>
        Parse Joining Documents
        <div>Educational Certificates</div>
        <div>Experience Letters</div>
        <div>Payslip Parsing</div>
      </div>
      <div>
        Experience Reimbursement Parsing
        <div>Invoice/Receipt Parsing</div>
        <div>Category Mapping</div>
        <div>Fraud & Duplication Detection</div>
        <div>Policy Compliance Check</div>
      </div>
    </>
  );
}