import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CampaignListResponse } from '../types';

export const CampaignList = () => {
  const [campaigns, setCampaigns] = useState<CampaignListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const data = await apiClient.listCampaigns();
      setCampaigns(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch campaigns');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      completed: 'badge-success',
      running: 'badge-warning',
      failed: 'badge-error',
      initialized: 'badge-info'
    };
    
    return `badge ${statusClasses[status as keyof typeof statusClasses] || 'badge-neutral'}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="loading loading-spinner loading-lg text-mm-primary"></div>
              <p className="mt-4 text-[var(--mm-gray-600)]">Loading campaigns...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="card-mm">
            <div className="p-6">
              <div className="alert alert-error">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
            <img src="/Marketmind.png" alt="MarketMinds AI Logo" className="w-32 h-20" />
            <div>
              <h1 className="text-3xl font-bold text-[var(--mm-gray-900)]">Campaigns</h1>
              <p className="text-[var(--mm-gray-600)]">Monitor and manage all your marketing campaigns</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link to="/generate" className="btn btn-mm-primary">
              Create New Campaign
            </Link>
            <Link to="/dashboard" className="btn btn-mm-secondary">
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Stats Overview */}
        {campaigns && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="stat-mm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-[var(--mm-gray-600)]">Total Campaigns</p>
                  <p className="text-2xl font-bold text-mm-primary">{campaigns.total}</p>
                </div>
                <div className="text-mm-primary">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="stat-mm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-[var(--mm-gray-600)]">Completed</p>
                  <p className="text-2xl font-bold text-[var(--mm-success)]">{campaigns.completed}</p>
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
                  <p className="text-2xl font-bold text-[var(--mm-warning)]">{campaigns.running}</p>
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
                  <p className="text-2xl font-bold text-[var(--mm-error)]">{campaigns.failed}</p>
                </div>
                <div className="text-[var(--mm-error)]">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Campaigns Table */}
        <div className="card-mm">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-6">All Campaigns</h2>
            
            {campaigns && campaigns.campaigns.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th className="text-[var(--mm-gray-700)]">Campaign ID</th>
                      <th className="text-[var(--mm-gray-700)]">Status</th>
                      <th className="text-[var(--mm-gray-700)]">Created</th>
                      <th className="text-[var(--mm-gray-700)]">Completed</th>
                      <th className="text-[var(--mm-gray-700)]">Execution Time</th>
                      <th className="text-[var(--mm-gray-700)]">Artifacts</th>
                      <th className="text-[var(--mm-gray-700)]">Created By</th>
                      <th className="text-[var(--mm-gray-700)]">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {campaigns.campaigns.map((campaign) => (
                      <tr key={campaign.campaign_id}>
                        <td className="font-mono text-sm">{campaign.campaign_id}</td>
                        <td>
                          <span className={getStatusBadge(campaign.status)}>
                            {campaign.status}
                          </span>
                        </td>
                        <td className="text-sm">
                          {new Date(campaign.created_at).toLocaleDateString()}
                        </td>
                        <td className="text-sm">
                          {campaign.completed_at 
                            ? new Date(campaign.completed_at).toLocaleDateString()
                            : '-'
                          }
                        </td>
                        <td className="text-sm">
                          {campaign.execution_time 
                            ? `${campaign.execution_time.toFixed(2)}s`
                            : '-'
                          }
                        </td>
                        <td className="text-sm">
                          <span className="badge badge-mm-secondary">
                            {campaign.artifacts_count}
                          </span>
                        </td>
                        <td className="text-sm">{campaign.created_by}</td>
                        <td>
                          <div className="flex gap-2">
                            <Link
                              to={`/campaign/${campaign.campaign_id}`}
                              className="btn btn-sm btn-mm-primary"
                            >
                              View
                            </Link>
                            {campaign.status === 'completed' && (
                              <Link
                                to={`/campaign/view/${campaign.campaign_id}`}
                                className="btn btn-sm btn-mm-secondary"
                              >
                                Website
                              </Link>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-[var(--mm-gray-400)] mb-4">
                  <svg className="w-24 h-24 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[var(--mm-gray-600)] mb-2">No Campaigns Yet</h3>
                <p className="text-[var(--mm-gray-500)] mb-6">
                  Get started by creating your first marketing campaign
                </p>
                <Link to="/generate" className="btn btn-mm-primary">
                  Create Your First Campaign
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
