import './index.css';
import DarkModeToggle from '../DarkModeToggle';

export default function Navbar() {
  return (
    <nav className="Navbar-Layout" aria-label="Main navigation">
      <h1 className="Title dm-serif">Neo HRMS</h1>
      <div className="Toggle" role="region" aria-label="Theme toggle">
        <DarkModeToggle />
      </div>
    </nav>
  );
}