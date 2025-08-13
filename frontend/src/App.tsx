import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';

// Components
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Dashboard } from './components/Dashboard';
import { CampaignGenerator } from './components/CampaignGenerator';
import { CampaignMonitor } from './components/CampaignMonitor';
import { CampaignList } from './components/CampaignList';
import { ProtectedRoute } from './components/ProtectedRoute';
import { CampaignView } from './components/CampaignView';
import { Nav } from './components/Nav';
import { useState, useEffect } from 'react';

function App() {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Nav theme={theme} onThemeChange={toggleTheme} />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
        
            <Route 
              path="/generate" 
              element={
                <ProtectedRoute>
                  <CampaignGenerator />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/campaigns" 
              element={
                <ProtectedRoute>
                  <CampaignList />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/campaign/:campaignId" 
              element={
                <ProtectedRoute>
                  <CampaignMonitor />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/campaign/view/:campaignId" 
              element={
                <ProtectedRoute>
                  <CampaignView />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 