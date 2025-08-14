import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CampaignResponse, CampaignStatus } from '../types';

export const CampaignMonitor = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const [campaign, setCampaign] = useState<CampaignResponse | null>(null);
  const [status, setStatus] = useState<CampaignStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (campaignId) {
      fetchCampaignData();
      const interval = setInterval(fetchCampaignData, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [campaignId]);

  const fetchCampaignData = async () => {
    try {
      const [campaignData, statusData] = await Promise.all([
        apiClient.getCampaign(campaignId!),
        apiClient.getCampaignStatus(campaignId!)
      ]);
      setCampaign(campaignData);
      setStatus(statusData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch campaign data');
    } finally {
      setLoading(false);
    }
  };

  const downloadWebsite = async () => {
    try {
      await apiClient.downloadWebsite(campaignId!);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download website');
    }
  };

  const downloadPDF = async () => {
    try {
      await apiClient.downloadPDF(campaignId!);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="loading loading-spinner loading-lg text-mm-primary"></div>
              <p className="mt-4 text-[var(--mm-gray-600)]">Loading campaign data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card-mm">
            <div className="p-6">
              <div className="alert alert-error">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error || 'Campaign not found'}</span>
              </div>
              <div className="mt-4">
                <Link to="/campaigns" className="btn btn-mm-primary">
                  Back to Campaigns
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Campaign Header */}
        <div className="card-mm">
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-mm-secondary mb-4">
                <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-[var(--mm-gray-900)]">MarketMinds AI Campaign Monitor</h1>
              <p className="text-[var(--mm-gray-600)]">Track your campaign generation progress in real-time</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="stat">
                <div className="stat-title">Campaign ID</div>
                <div className="stat-value text-lg font-mono">{campaign.campaign_id}</div>
              </div>
              <div className="stat">
                <div className="stat-title">Created</div>
                <div className="stat-value text-lg">{new Date(campaign.created_at).toLocaleString()}</div>
              </div>
              <div className="stat">
                <div className="stat-title">Created By</div>
                <div className="stat-value text-lg">{campaign.created_by}</div>
              </div>
              {campaign.execution_time && (
                <div className="stat">
                  <div className="stat-title">Execution Time</div>
                  <div className="stat-value text-lg">{campaign.execution_time.toFixed(2)}s</div>
                </div>
              )}
              {campaign.quality_score && (
                <div className="stat">
                  <div className="stat-title">Quality Score</div>
                  <div className="stat-value text-lg">{campaign.quality_score}</div>
                </div>
              )}
              {campaign.revision_count && (
                <div className="stat">
                  <div className="stat-title">Revisions</div>
                  <div className="stat-value text-lg">{campaign.revision_count}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Progress Information */}
        {status?.progress && (
          <div className="card-mm">
            <div className="p-6">
              <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-4">Progress</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="stat">
                  <div className="stat-title">Artifacts Generated</div>
                  <div className="stat-value text-mm-primary">{status.progress.artifacts_generated}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Revision Count</div>
                  <div className="stat-value text-mm-secondary">{status.progress.revision_count}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Execution Time</div>
                  <div className="stat-value text-[var(--mm-gray-700)]">{status.progress.execution_time?.toFixed(2)}s</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Download Section */}
        {campaign.status === 'completed' && (
          <div className="card-mm">
            <div className="p-6">
              <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-4">Download Results</h3>
              <div className="flex flex-wrap gap-4 mb-6">
                <button onClick={downloadWebsite} className="btn btn-mm-primary">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download Website
                </button>
                <button onClick={downloadPDF} className="btn btn-mm-secondary">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download PDF Report
                </button>
              </div>
              
              <div className="collapse collapse-arrow bg-[var(--mm-gray-100)]">
                <input type="checkbox" /> 
                <div className="collapse-title text-lg font-medium text-[var(--mm-gray-900)]">
                  Generated Artifacts
                </div>
                <div className="collapse-content">
                  <div className="space-y-2">
                    {Object.entries(campaign.artifacts).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-2 bg-white rounded">
                        <span className="font-medium text-[var(--mm-gray-700)]">{key}</span>
                        <span className="text-[var(--mm-gray-600)]">{typeof value === 'string' ? value : 'Generated'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Status Display */}
        <div className="card-mm">
          <div className="p-6">
            <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-4">Current Status</h3>
            <div className="flex items-center gap-4">
              <div className={`badge badge-lg ${
                campaign.status === 'completed' ? 'badge-success' :
                campaign.status === 'running' ? 'badge-warning' :
                campaign.status === 'failed' ? 'badge-error' :
                'badge-info'
              }`}>
                {campaign.status.toUpperCase()}
              </div>
              <div className="text-[var(--mm-gray-600)]">
                {campaign.status === 'completed' && 'Campaign generation completed successfully!'}
                {campaign.status === 'running' && 'Campaign is currently being generated...'}
                {campaign.status === 'failed' && 'Campaign generation failed. Please try again.'}
                {campaign.status === 'initialized' && 'Campaign has been initialized and is waiting to start.'}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-4">
          <Link to="/campaigns" className="btn btn-mm-secondary">
            Back to Campaigns
          </Link>
          <Link to="/generate" className="btn btn-mm-primary">
            Create New Campaign
          </Link>
        </div>
      </div>
    </div>
  );
}; 