import './index.css'

export default function Sidebar() {
  return (
    <div className="Sidebar-layout">
      {/* Top Menu Button */}
      <div className="Menu-Button">
        menu
      </div>

      {/* Sections */}
      <div className="Sections">
        <div>section-1</div>
        <div>section-2</div>
        <div>section-3</div>
      </div>

      {/* Bottom Settings */}
      <div className="Settings">
        Settings or something else
      </div>
    </div>
  );
}
