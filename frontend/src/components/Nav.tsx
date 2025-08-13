import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const Nav: React.FC = () => {
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
    <nav style={{
      background: '#2c3e50',
      padding: '0 20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        minHeight: '60px'
      }}>
        {/* Logo/Brand */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Link to="/" style={{
            textDecoration: 'none',
            color: 'white',
            fontSize: '20px',
            fontWeight: 'bold'
          }}>
            🎨 Campaign Generator
          </Link>
        </div>

        {/* Navigation Links */}
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <Link 
            to="/" 
            style={{
              textDecoration: 'none',
              color: isActive('/') ? '#3498db' : 'white',
              padding: '8px 16px',
              borderRadius: '4px',
              transition: 'all 0.2s ease',
              background: isActive('/') ? 'rgba(52, 152, 219, 0.1)' : 'transparent'
            }}
          >
            Dashboard
          </Link>
          
          <Link 
            to="/generate" 
            style={{
              textDecoration: 'none',
              color: isActive('/generate') ? '#3498db' : 'white',
              padding: '8px 16px',
              borderRadius: '4px',
              transition: 'all 0.2s ease',
              background: isActive('/generate') ? 'rgba(52, 152, 219, 0.1)' : 'transparent'
            }}
          >
            Generate Campaign
          </Link>
          
          <Link 
            to="/campaigns" 
            style={{
              textDecoration: 'none',
              color: isActive('/campaigns') ? '#3498db' : 'white',
              padding: '8px 16px',
              borderRadius: '4px',
              transition: 'all 0.2s ease',
              background: isActive('/campaigns') ? 'rgba(52, 152, 219, 0.1)' : 'transparent'
            }}
          >
            View Campaigns
          </Link>
        </div>

        {/* User Menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: 'white', fontSize: '14px' }}>
              {user.full_name || user.username}
            </div>
            <div style={{ color: '#bdc3c7', fontSize: '12px' }}>
              {user.role}
            </div>
          </div>
          
          <button 
            onClick={handleLogout}
            style={{
              background: 'transparent',
              border: '1px solid #e74c3c',
              color: '#e74c3c',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              fontSize: '14px'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#e74c3c';
              e.currentTarget.style.color = 'white';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = '#e74c3c';
            }}
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}; 