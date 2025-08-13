import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import './App.css';

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

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Nav />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
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
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 