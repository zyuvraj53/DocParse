import './index.css'
import DarkModeToggle from '../DarkModeToggle';

export default function Navbar(){
  return (
    <div className="Navbar-Layout">
      <div className='Title dm-serif'>
        Neo HRMS
      </div>
      <div className='Toggle'>
        <DarkModeToggle/>
      </div>
    </div>
  )
}