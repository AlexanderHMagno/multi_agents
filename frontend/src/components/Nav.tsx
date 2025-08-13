import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

interface NavProps {
  theme: string;
  onThemeChange: (theme: string) => void;
}

export const Nav = ({ theme, onThemeChange }: NavProps) => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  // Note: theme parameter is kept for future use (e.g., showing current theme indicator)

  return (
    <div className="navbar bg-base-100 shadow-lg">
      <div className="navbar-start">
        <div className="dropdown">
          <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </div>
          <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/generate">Generate Campaign</Link></li>
            <li><Link to="/campaigns">View Campaigns</Link></li>
          </ul>
        </div>
        <Link to="/dashboard" className="btn btn-ghost text-xl font-bold text-primary">
          <img src="/Marketmind.png" alt="MarketMinds AI Logo" className="w-32 h-20 mr-2" />
          {/* MarketMinds AI */}
        </Link>
      </div>
      
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/generate">Generate Campaign</Link></li>
          <li><Link to="/campaigns">View Campaigns</Link></li>
        </ul>
      </div>
      
      <div className="navbar-end">
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <div className="dropdown dropdown-end">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-1a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2V5zM21 12a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2v-1a2 2 0 00-2-2zM21 19a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2v-1a2 2 0 00-2-2z" />
              </svg>
            </div>
            <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
              <li><button onClick={() => onThemeChange('light')} className={theme === 'light' ? 'active' : ''}>Light</button></li>
              <li><button onClick={() => onThemeChange('dark')} className={theme === 'dark' ? 'active' : ''}>Dark</button></li>
              <li><button onClick={() => onThemeChange('corporate')} className={theme === 'corporate' ? 'active' : ''}>Corporate</button></li>
              <li><button onClick={() => onThemeChange('business')} className={theme === 'business' ? 'active' : ''}>Business</button></li>
              <li><button onClick={() => onThemeChange('synthwave')} className={theme === 'synthwave' ? 'active' : ''}>Synthwave</button></li>
              <li><button onClick={() => onThemeChange('retro')} className={theme === 'retro' ? 'active' : ''}>Retro</button></li>
              <li><button onClick={() => onThemeChange('cyberpunk')} className={theme === 'cyberpunk' ? 'active' : ''}>Cyberpunk</button></li>
              <li><button onClick={() => onThemeChange('valentine')} className={theme === 'valentine' ? 'active' : ''}>Valentine</button></li>
              <li><button onClick={() => onThemeChange('halloween')} className={theme === 'halloween' ? 'active' : ''}>Halloween</button></li>
              <li><button onClick={() => onThemeChange('garden')} className={theme === 'garden' ? 'active' : ''}>Garden</button></li>
              <li><button onClick={() => onThemeChange('forest')} className={theme === 'forest' ? 'active' : ''}>Forest</button></li>
              <li><button onClick={() => onThemeChange('aqua')} className={theme === 'aqua' ? 'active' : ''}>Aqua</button></li>
              <li><button onClick={() => onThemeChange('lofi')} className={theme === 'lofi' ? 'active' : ''}>Lo-Fi</button></li>
              <li><button onClick={() => onThemeChange('pastel')} className={theme === 'pastel' ? 'active' : ''}>Pastel</button></li>
              <li><button onClick={() => onThemeChange('fantasy')} className={theme === 'fantasy' ? 'active' : ''}>Fantasy</button></li>
              <li><button onClick={() => onThemeChange('wireframe')} className={theme === 'wireframe' ? 'active' : ''}>Wireframe</button></li>
              <li><button onClick={() => onThemeChange('black')} className={theme === 'black' ? 'active' : ''}>Black</button></li>
              <li><button onClick={() => onThemeChange('luxury')} className={theme === 'luxury' ? 'active' : ''}>Luxury</button></li>
              <li><button onClick={() => onThemeChange('dracula')} className={theme === 'dracula' ? 'active' : ''}>Dracula</button></li>
              <li><button onClick={() => onThemeChange('cmyk')} className={theme === 'cmyk' ? 'active' : ''}>CMYK</button></li>
              <li><button onClick={() => onThemeChange('autumn')} className={theme === 'autumn' ? 'active' : ''}>Autumn</button></li>
              <li><button onClick={() => onThemeChange('acid')} className={theme === 'acid' ? 'active' : ''}>Acid</button></li>
              <li><button onClick={() => onThemeChange('lemonade')} className={theme === 'lemonade' ? 'active' : ''}>Lemonade</button></li>
              <li><button onClick={() => onThemeChange('night')} className={theme === 'night' ? 'active' : ''}>Night</button></li>
              <li><button onClick={() => onThemeChange('coffee')} className={theme === 'coffee' ? 'active' : ''}>Coffee</button></li>
              <li><button onClick={() => onThemeChange('winter')} className={theme === 'winter' ? 'active' : ''}>Winter</button></li>
              <li><button onClick={() => onThemeChange('dim')} className={theme === 'dim' ? 'active' : ''}>Dim</button></li>
              <li><button onClick={() => onThemeChange('nord')} className={theme === 'nord' ? 'active' : ''}>Nord</button></li>
              <li><button onClick={() => onThemeChange('sunset')} className={theme === 'sunset' ? 'active' : ''}>Sunset</button></li>
              <li><button onClick={() => onThemeChange('caramellatte')} className={theme === 'caramellatte' ? 'active' : ''}>Caramel Latte</button></li>
              <li><button onClick={() => onThemeChange('abyss')} className={theme === 'abyss' ? 'active' : ''}>Abyss</button></li>
              <li><button onClick={() => onThemeChange('silk')} className={theme === 'silk' ? 'active' : ''}>Silk</button></li>
            </ul>
          </div>
          
          {/* User Menu */}
          <div className="dropdown dropdown-end">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle avatar">
              <div className="w-10 rounded-full">
                <div className="bg-primary text-primary-content rounded-full w-10 h-10 flex items-center justify-center text-lg font-bold">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
              </div>
            </div>
            <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li className="menu-title">
                <span className="text-sm opacity-70">Signed in as</span>
                <span className="font-semibold">{user?.username}</span>
              </li>
              <div className="divider my-1"></div>
              <li><button onClick={handleLogout}>Logout</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}; 