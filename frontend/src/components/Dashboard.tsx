import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import { ThemeSwitcher } from './ThemeSwitcher';

export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
           
          </div>
          <div className="flex items-center gap-3">
            <ThemeSwitcher />
            <Link to="/generate" className="btn btn-mm-primary">
              Create New Campaign
            </Link>
            <Link to="/campaigns" className="btn btn-mm-secondary">
              View All Campaigns
            </Link>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="stat-mm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Total Campaigns</p>
                <p className="text-2xl font-bold text-mm-primary">12</p>
                <p className="text-xs text-[var(--mm-gray-500)]">↗︎ 14% more than last month</p>
              </div>
              <div className="text-mm-primary">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="stat-mm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Completed</p>
                <p className="text-2xl font-bold text-[var(--mm-gray-900)]">8</p>
                <p className="text-xs text-[var(--mm-gray-500)]">↗︎ 67% success rate</p>
              </div>
              <div className="text-[var(--mm-success)]">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="stat-mm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Running</p>
                <p className="text-2xl font-bold text-[var(--mm-gray-900)]">3</p>
                <p className="text-xs text-[var(--mm-gray-500)]">↘︎ 2 completed today</p>
              </div>
              <div className="text-[var(--mm-warning)]">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="stat-mm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Failed</p>
                <p className="text-2xl font-bold text-[var(--mm-gray-900)]">1</p>
                <p className="text-xs text-[var(--mm-gray-500)]">↘︎ 8% failure rate</p>
              </div>
              <div className="text-[var(--mm-error)]">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Generate Campaign Card */}
          <div className="card-mm">
            <div className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="text-mm-primary">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[var(--mm-gray-900)]">Generate New Campaign</h3>
                  <p className="text-[var(--mm-gray-600)]">Create a comprehensive marketing campaign using MarketMinds AI agents</p>
                </div>
              </div>
              <div className="flex justify-end">
                <Link to="/generate" className="btn btn-mm-primary">
                  Start Campaign Generation
                </Link>
              </div>
            </div>
          </div>

          {/* View Campaigns Card */}
          <div className="card-mm">
            <div className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="text-mm-primary">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[var(--mm-gray-900)]">View Campaigns</h3>
                  <p className="text-[var(--mm-gray-600)]">Monitor your existing campaigns and download results (website coming soon)</p>
                </div>
              </div>
              <div className="flex justify-end">
                <Link to="/campaigns" className="btn btn-mm-primary">
                  View All Campaigns
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity & Quick Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Recent Campaigns */}
          <div className="card-mm lg:col-span-2">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-[var(--mm-gray-900)] mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-mm-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recent Campaigns
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-[var(--mm-gray-50)] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-[var(--mm-success)] rounded-full"></div>
                    <div>
                      <p className="font-medium text-[var(--mm-gray-900)]">Summer Product Launch</p>
                      <p className="text-sm text-[var(--mm-gray-500)]">Completed 2 hours ago</p>
                    </div>
                  </div>
                  <span className="badge badge-mm-primary">Completed</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-[var(--mm-gray-50)] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-[var(--mm-warning)] rounded-full"></div>
                    <div>
                      <p className="font-medium text-[var(--mm-gray-900)]">Holiday Campaign</p>
                      <p className="text-sm text-[var(--mm-gray-500)]">Running - 75% complete</p>
                    </div>
                  </div>
                  <span className="badge badge-mm-secondary">Running</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-[var(--mm-gray-50)] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-[var(--mm-error)] rounded-full"></div>
                    <div>
                      <p className="font-medium text-[var(--mm-gray-900)]">Brand Refresh</p>
                      <p className="text-sm text-[var(--mm-gray-500)]">Failed - 1 hour ago</p>
                    </div>
                  </div>
                  <span className="badge bg-red-100 text-red-800">Failed</span>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="card-mm">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-[var(--mm-gray-900)] mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-mm-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Performance
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-[var(--mm-gray-600)]">Success Rate</span>
                    <span className="font-medium text-[var(--mm-gray-900)]">67%</span>
                  </div>
                  <div className="w-full bg-[var(--mm-gray-200)] rounded-full h-2">
                    <div className="bg-[var(--mm-success)] h-2 rounded-full" style={{ width: '67%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-[var(--mm-gray-600)]">Avg. Generation Time</span>
                    <span className="font-medium text-[var(--mm-gray-900)]">4.2 min</span>
                  </div>
                  <div className="w-full bg-[var(--mm-gray-200)] rounded-full h-2">
                    <div className="bg-mm-primary h-2 rounded-full" style={{ width: '70%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-[var(--mm-gray-600)]">Quality Score</span>
                    <span className="font-medium text-[var(--mm-gray-900)]">8.7/10</span>
                  </div>
                  <div className="w-full bg-[var(--mm-gray-200)] rounded-full h-2">
                    <div className="bg-mm-secondary h-2 rounded-full" style={{ width: '87%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Information */}
        <div className="card-mm">
          <div className="p-6">
            <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2 text-[var(--mm-gray-600)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Account Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[var(--mm-gray-100)] rounded-lg p-4">
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Username</p>
                <p className="text-lg font-mono text-[var(--mm-gray-900)]">{user?.username}</p>
              </div>
              <div className="bg-[var(--mm-gray-100)] rounded-lg p-4">
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Email</p>
                <p className="text-lg text-[var(--mm-gray-900)]">{user?.email}</p>
              </div>
              <div className="bg-[var(--mm-gray-100)] rounded-lg p-4">
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Role</p>
                <div className="mt-1">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    user?.role === 'admin' 
                      ? 'badge-mm-primary' 
                      : 'badge-mm-secondary'
                  }`}>
                    {user?.role}
                  </span>
                </div>
              </div>
              <div className="bg-[var(--mm-gray-100)] rounded-lg p-4">
                <p className="text-sm font-medium text-[var(--mm-gray-600)]">Status</p>
                <div className="mt-1">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    user?.disabled 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {user?.disabled ? 'Disabled' : 'Active'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Start Guide */}
        <div className="card-mm">
          <div className="p-6">
            <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-6 flex items-center">
              <svg className="w-6 h-6 mr-2 text-[var(--mm-gray-600)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Quick Start Guide
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-mm-primary-light text-mm-primary rounded-full flex items-center justify-center text-sm font-medium">1</div>
                  <div>
                    <h4 className="font-medium text-[var(--mm-gray-900)]">Start Campaign Generation</h4>
                    <p className="text-sm text-[var(--mm-gray-600)]">Click "Create New Campaign" to begin your first campaign</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-mm-secondary-light text-mm-secondary rounded-full flex items-center justify-center text-sm font-medium">2</div>
                  <div>
                    <h4 className="font-medium text-[var(--mm-gray-900)]">Fill Campaign Brief</h4>
                    <p className="text-sm text-[var(--mm-gray-600)]">Provide detailed requirements for your marketing campaign</p>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-medium">3</div>
                  <div>
                    <h4 className="font-medium text-[var(--mm-gray-900)]">AI Processing</h4>
                    <p className="text-sm text-[var(--mm-gray-600)]">Wait for MarketMinds AI agents to generate your campaign</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-medium">4</div>
                  <div>
                    <h4 className="font-medium text-[var(--mm-gray-900)]">Monitor & Download</h4>
                    <p className="text-sm text-[var(--mm-gray-600)]">Track progress and download results when complete</p>
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