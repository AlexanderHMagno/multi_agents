import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-base-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="hero bg-base-100 rounded-box shadow-lg mb-8">
          <div className="hero-content text-center">
            <div className="max-w-2xl">
              <h1 className="text-5xl font-bold text-primary mb-4">🎨</h1>
              <h2 className="text-4xl font-bold">Campaign Generator Dashboard</h2>
              <p className="py-6 text-lg opacity-70">
                Welcome back, <span className="font-semibold text-primary">{user?.full_name || user?.username}</span>! 
                Ready to create amazing campaigns?
              </p>
            </div>
          </div>
        </div>

        {/* Main Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Generate Campaign Card */}
          <div className="card bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20 hover:shadow-xl transition-all duration-300">
            <div className="card-body text-center">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="card-title justify-center text-xl">Generate New Campaign</h3>
              <p className="text-base-content/70 mb-6">
                Create a comprehensive marketing campaign using our AI agents.
              </p>
              <Link to="/generate" className="btn btn-primary btn-wide">
                Start Campaign Generation
              </Link>
            </div>
          </div>

          {/* View Campaigns Card */}
          <div className="card bg-gradient-to-br from-secondary/10 to-secondary/5 border border-secondary/20 hover:shadow-xl transition-all duration-300">
            <div className="card-body text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="card-title justify-center text-xl">View Campaigns</h3>
              <p className="text-base-content/70 mb-6">
                Monitor your existing campaigns and download results.
              </p>
              <Link to="/campaigns" className="btn btn-secondary btn-wide">
                View All Campaigns
              </Link>
            </div>
          </div>

          {/* Account Info Card */}
          <div className="card bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20 hover:shadow-xl transition-all duration-300">
            <div className="card-body text-center">
              <div className="text-4xl mb-4">👤</div>
              <h3 className="card-title justify-center text-xl">Account Info</h3>
              <div className="space-y-2 text-sm text-left">
                <div className="flex justify-between">
                  <span className="font-medium">Username:</span>
                  <span className="badge badge-outline">{user?.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Email:</span>
                  <span className="badge badge-outline">{user?.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Role:</span>
                  <span className={`badge ${user?.role === 'admin' ? 'badge-primary' : 'badge-secondary'}`}>
                    {user?.role}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Status:</span>
                  <span className={`badge ${user?.disabled ? 'badge-error' : 'badge-success'}`}>
                    {user?.disabled ? 'Disabled' : 'Active'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Start Guide */}
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body">
            <h3 className="card-title text-2xl mb-6 text-center">🎯 Quick Start Guide</h3>
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="badge badge-primary badge-lg">1</div>
                    <div>
                      <h4 className="font-semibold">Start Campaign Generation</h4>
                      <p className="text-sm text-base-content/70">Click "Start Campaign Generation" to create a new campaign</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="badge badge-secondary badge-lg">2</div>
                    <div>
                      <h4 className="font-semibold">Fill Campaign Brief</h4>
                      <p className="text-sm text-base-content/70">Provide detailed requirements for your marketing campaign</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="badge badge-accent badge-lg">3</div>
                    <div>
                      <h4 className="font-semibold">AI Processing</h4>
                      <p className="text-sm text-base-content/70">Wait for our AI agents to generate your campaign</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="badge badge-info badge-lg">4</div>
                    <div>
                      <h4 className="font-semibold">Monitor & Download</h4>
                      <p className="text-sm text-base-content/70">Track progress and download results when complete</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 