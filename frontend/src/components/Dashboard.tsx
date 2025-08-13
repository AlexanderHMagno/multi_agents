import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-base-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
            <img src="/Marketmind.png" alt="MarketMinds AI Logo" className="w-32 h-20" />
            <div>
              <p className="text-base-content/70 mt-2">
                Welcome back, <span className="font-semibold text-primary">{user?.full_name || user?.username}</span>!
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link to="/generate" className="btn btn-primary">
              Create New Campaign
            </Link>
            <Link to="/campaigns" className="btn btn-outline">
              View All Campaigns
            </Link>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-primary">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="stat-title">Total Campaigns</div>
            <div className="stat-value text-primary">12</div>
            <div className="stat-desc">↗︎ 14% more than last month</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-success">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Completed</div>
            <div className="stat-value text-success">8</div>
            <div className="stat-desc">↗︎ 67% success rate</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-warning">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Running</div>
            <div className="stat-value text-warning">3</div>
            <div className="stat-desc">↘︎ 2 completed today</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-error">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Failed</div>
            <div className="stat-value text-error">1</div>
            <div className="stat-desc">↘︎ 8% failure rate</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Generate Campaign Card */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="flex items-center gap-4 mb-4">
                <div className="text-primary">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="card-title text-xl">Generate New Campaign</h3>
                  <p className="text-base-content/70">Create a comprehensive marketing campaign using MarketMinds AI agents</p>
                </div>
              </div>
              <div className="card-actions justify-end">
                <Link to="/generate" className="btn btn-primary">
                  Start Campaign Generation
                </Link>
              </div>
            </div>
          </div>

          {/* View Campaigns Card */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="flex items-center gap-4 mb-4">
                <div className="text-secondary">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="card-title text-xl">View Campaigns</h3>
                  <p className="text-base-content/70">Monitor your existing campaigns and download results</p>
                </div>
              </div>
              <div className="card-actions justify-end">
                <Link to="/campaigns" className="btn btn-secondary">
                  View All Campaigns
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Account Information */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-xl mb-4">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Account Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="stat bg-base-200 rounded-box">
                <div className="stat-title">Username</div>
                <div className="stat-value text-lg font-mono">{user?.username}</div>
              </div>
              <div className="stat bg-base-200 rounded-box">
                <div className="stat-title">Email</div>
                <div className="stat-value text-lg">{user?.email}</div>
              </div>
              <div className="stat bg-base-200 rounded-box">
                <div className="stat-title">Role</div>
                <div className="stat-value text-lg">
                  <div className={`badge ${user?.role === 'admin' ? 'badge-primary' : 'badge-secondary'} badge-lg`}>
                    {user?.role}
                  </div>
                </div>
              </div>
              <div className="stat bg-base-200 rounded-box">
                <div className="stat-title">Status</div>
                <div className="stat-value text-lg">
                  <div className={`badge ${user?.disabled ? 'badge-error' : 'badge-success'} badge-lg`}>
                    {user?.disabled ? 'Disabled' : 'Active'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Start Guide */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-xl mb-6">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Quick Start Guide
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="badge badge-primary badge-lg">1</div>
                  <div>
                    <h4 className="font-semibold">Start Campaign Generation</h4>
                    <p className="text-sm text-base-content/70">Click "Create New Campaign" to begin your first campaign</p>
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
                    <p className="text-sm text-base-content/70">Wait for MarketMinds AI agents to generate your campaign</p>
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
  );
}; 