import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎨 Campaign Generator Dashboard</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span>Welcome, {user?.full_name || user?.username}!</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="main-content">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px', 
          marginTop: '30px' 
        }}>
          <div className="form-container">
            <h3>🚀 Generate New Campaign</h3>
            <p>Create a comprehensive marketing campaign using our AI agents.</p>
            <Link to="/generate" className="btn">
              Start Campaign Generation
            </Link>
          </div>

          <div className="form-container">
            <h3>📊 View Campaigns</h3>
            <p>Monitor your existing campaigns and download results.</p>
            <Link to="/campaigns" className="btn">
              View All Campaigns
            </Link>
          </div>

          <div className="form-container">
            <h3>👤 Account Info</h3>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Role:</strong> {user?.role}</p>
            <p><strong>Status:</strong> {user?.disabled ? 'Disabled' : 'Active'}</p>
          </div>
        </div>

        <div style={{ marginTop: '40px', textAlign: 'center' }}>
          <h3>🎯 Quick Start Guide</h3>
          <ol style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
            <li>Click "Start Campaign Generation" to create a new campaign</li>
            <li>Fill out the campaign brief with your requirements</li>
            <li>Submit and wait for the AI agents to generate your campaign</li>
            <li>Monitor progress and download results when complete</li>
          </ol>
        </div>
      </div>
    </div>
  );
}; 