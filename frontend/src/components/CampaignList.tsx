import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CampaignListResponse } from '../types';

export const CampaignList: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const data = await apiClient.listCampaigns();
      setCampaigns(data);
    } catch (err: any) {
      setError(err.detail || 'Failed to fetch campaigns');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'warning';
      case 'failed':
        return 'error';
      case 'initialized':
        return 'info';
      default:
        return 'neutral';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body text-center">
              <span className="loading loading-spinner loading-lg text-primary"></span>
              <h3 className="text-xl font-semibold mt-4">Loading campaigns...</h3>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="alert alert-error shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Error</h3>
              <div className="text-xs">{error}</div>
            </div>
            <button onClick={fetchCampaigns} className="btn btn-sm">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!campaigns || campaigns.campaigns.length === 0) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body text-center">
              <h2 className="text-2xl font-bold mb-4">No Campaigns Found</h2>
              <p className="text-base-content/70 mb-6">You haven't created any campaigns yet.</p>
              <Link to="/generate" className="btn btn-primary">
                Create Your First Campaign
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
            <img src="/Marketmind.png" alt="MarketMinds AI Logo" className="w-32 h-20" />
            <div>
              <p className="text-base-content/70 mt-2">Monitor and manage your AI-generated campaigns</p>
            </div>
          </div>
          <Link to="/generate" className="btn btn-primary">
            Create New Campaign
          </Link>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-success">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="stat-title">Total Campaigns</div>
            <div className="stat-value text-success">{campaigns.total}</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-success">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Completed</div>
            <div className="stat-value text-success">{campaigns.completed}</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-warning">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Running</div>
            <div className="stat-value text-warning">{campaigns.running}</div>
          </div>
          
          <div className="stat bg-base-100 shadow-lg rounded-box">
            <div className="stat-figure text-error">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-title">Failed</div>
            <div className="stat-value text-error">{campaigns.failed}</div>
          </div>
        </div>

        {/* Campaigns Table */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body p-0">
            <div className="overflow-x-auto">
              <table className="table table-zebra w-full">
                <thead>
                  <tr>
                    <th className="bg-base-200">Campaign ID</th>
                    <th className="bg-base-200">Status</th>
                    <th className="bg-base-200">Created</th>
                    <th className="bg-base-200">Execution Time</th>
                    <th className="bg-base-200">Artifacts</th>
                    <th className="bg-base-200">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.campaigns.map((campaign) => (
                    <tr key={campaign.campaign_id} className="hover">
                      <td className="font-mono text-xs">
                        {campaign.campaign_id}
                      </td>
                      <td>
                        <div className={`badge badge-${getStatusColor(campaign.status)} badge-lg`}>
                          {campaign.status.toUpperCase()}
                        </div>
                      </td>
                      <td>
                        {formatDate(campaign.created_at)}
                      </td>
                      <td>
                        {campaign.execution_time 
                          ? `${campaign.execution_time.toFixed(2)}s`
                          : '-'
                        }
                      </td>
                      <td>
                        <div className="badge badge-outline">{campaign.artifacts_count}</div>
                      </td>
                      <td>
                        <div className="flex gap-2">
                          <Link 
                            to={`/campaign/${campaign.campaign_id}`}
                            className="btn btn-sm btn-ghost"
                          >
                            View
                          </Link>
                          {campaign.status === 'completed' && (
                            <Link 
                              to={`/campaign/view/${campaign.campaign_id}`}
                              className="btn btn-sm btn-primary"
                            >
                              Preview
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="text-center mt-8">
          <button onClick={fetchCampaigns} className="btn btn-secondary btn-wide">
            Refresh Campaigns
          </button>
        </div>
      </div>
    </div>
  );
};
