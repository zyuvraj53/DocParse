import { Routes, Route, Link } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import ResumeParser from "./pages/ResumeParser";
import JoiningDocParser from "./pages/JoiningDocParser";
import JoiningDocParserHome from "./pages/JoiningDocParser";
import EdCertParser from "./pages/JoiningDocParser/EdCertParser";
import ExperienceLetterParser from "./pages/JoiningDocParser/ExperienceLetterParser";
import PayslipParser from "./pages/JoiningDocParser/PayslipParser";
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
            <Route path="/JoiningDocParser/*" element={<JoiningDocParser />}>
              <Route index element={<JoiningDocParserHome />} />
              <Route path="EdCertParser" element={<EdCertParser />} />
              <Route path="ExperienceLetterParser" element={<ExperienceLetterParser />} />
              <Route path="PayslipParser" element={<PayslipParser />} />
            </Route>
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
        <Link to="/JoiningDocParser" className="nav-link">
          Parse Joining Documents
        </Link>
        <div className="Viewport-Subsection">
          <Link to="/JoiningDocParser/EdCertParser">Educational Certificates</Link>
        </div>
        <div className="Viewport-Subsection">
          <Link to="/JoiningDocParser/ExperienceLetterParser">Experience Letters</Link>
        </div>
        <div className="Viewport-Subsection">
          <Link to="/JoiningDocParser/PayslipParser">Payslip Parsing</Link>
        </div>
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