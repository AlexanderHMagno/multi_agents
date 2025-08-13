import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface NavProps {
  theme: string;
  onThemeChange: () => void;
}

export const Nav: React.FC<NavProps> = ({ theme, onThemeChange }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  if (!user) {
    return null; // Don't show nav for unauthenticated users
  }

  return (
    <div className="navbar bg-base-100 shadow-lg border-b border-base-300">
      <div className="navbar-start">
        <div className="dropdown">
          <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16"></path>
            </svg>
          </div>
          <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><Link to="/" className={isActive('/') ? 'active' : ''}>Dashboard</Link></li>
            <li><Link to="/generate" className={isActive('/generate') ? 'active' : ''}>Generate Campaign</Link></li>
            <li><Link to="/campaigns" className={isActive('/campaigns') ? 'active' : ''}>View Campaigns</Link></li>
          </ul>
        </div>
        <Link to="/" className="btn btn-ghost text-xl">
          🎨 Campaign Generator
        </Link>
      </div>
      
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">
          <li>
            <Link 
              to="/" 
              className={`${isActive('/') ? 'active' : ''}`}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link 
              to="/generate" 
              className={`${isActive('/generate') ? 'active' : ''}`}
            >
              Generate Campaign
            </Link>
          </li>
          <li>
            <Link 
              to="/campaigns" 
              className={`${isActive('/campaigns') ? 'active' : ''}`}
            >
              View Campaigns
            </Link>
          </li>
        </ul>
      </div>
      
      <div className="navbar-end">
        {/* Theme Toggle Button */}
        <button
          onClick={onThemeChange}
          className="btn btn-ghost btn-circle btn-sm mr-2"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        
        <div className="dropdown dropdown-end">
          <div tabIndex={0} role="button" className="btn btn-ghost btn-circle avatar">
            <div className="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center">
              <span className="text-lg font-bold">
                {(user.full_name || user.username).charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
          <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li className="menu-title">
              <span className="font-semibold">{user.full_name || user.username}</span>
            </li>
            <li className="menu-title">
              <span className="text-sm opacity-70">{user.role}</span>
            </li>
            <div className="divider my-1"></div>
            <li>
              <button onClick={handleLogout} className="text-error">
                Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}; 