import React, { useState } from 'react';
import './index.css';
import Hamburger from '../Hamburger';
import { FileUser, ScrollText, Receipt } from 'lucide-react';

export default function Sidebar() {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCheckboxChange = (e) => {
    setIsExpanded(e.target.checked);
  };

  return (
    <div className={`Sidebar-layout ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* Top Menu Button */}
      <div className="Menu-Button">
        <Hamburger onChange={handleCheckboxChange} />
      </div>

      {/* Sections */}
      <div className="Sections">
        <div className="section-item" title="Parse Resumes">
          <div className="icon-container">
            <FileUser size={20} />
          </div>
          <span className="section-text">Parse Resumes</span>
        </div>
        <div className="section-item" title="Parse Joining Documents">
          <div className="icon-container">
            <ScrollText size={20} />
          </div>
          <span className="section-text">Parse Joining Documents</span>
        </div>
        <div className="section-item" title="Parse Receipts">
          <div className="icon-container">
            <Receipt size={20} />
          </div>
          <span className="section-text">Parse Receipts</span>
        </div>
      </div>

      {/* Bottom Settings */}
      {/* <div className="Settings">
        Settings or something else
      </div> */}
    </div>
  );
}