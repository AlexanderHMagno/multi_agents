import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CampaignResponse, CampaignStatus } from '../types';

export const CampaignMonitor = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const [campaign, setCampaign] = useState<CampaignResponse | null>(null);
  const [status, setStatus] = useState<CampaignStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!campaignId) return;

    const fetchCampaign = async () => {
      try {
        const [campaignData, statusData] = await Promise.all([
          apiClient.getCampaign(campaignId),
          apiClient.getCampaignStatus(campaignId)
        ]);
        setCampaign(campaignData);
        setStatus(statusData);
      } catch (err: any) {
        setError(err.detail || 'Failed to fetch campaign');
      } finally {
        setLoading(false);
      }
    };

    fetchCampaign();
    
    // Poll for status updates every 5 seconds if campaign is running
    const interval = setInterval(() => {
      if (status?.status === 'running') {
        fetchCampaign();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [campaignId, status?.status]);

  const downloadWebsite = async () => {
    if (!campaignId) return;
    
    try {
      const blob = await apiClient.downloadWebsite(campaignId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${campaignId}_website.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download website');
    }
  };

  const downloadPDF = async () => {
    if (!campaignId) return;
    
    try {
      const blob = await apiClient.downloadPDF(campaignId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${campaignId}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body text-center">
              <span className="loading loading-spinner loading-lg text-primary"></span>
              <h3 className="text-xl font-semibold mt-4">Loading campaign...</h3>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="alert alert-error shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Error</h3>
              <div className="text-xs">{error}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="min-h-screen bg-base-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="alert alert-error shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Campaign Not Found</h3>
              <div className="text-xs">The requested campaign could not be found.</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'failed': return 'error';
      default: return 'warning';
    }
  };

  return (
    <div className="min-h-screen bg-base-200 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Campaign Header */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="card-title text-2xl">Campaign Status</h2>
              <div className={`badge badge-${getStatusColor(campaign.status)} badge-lg`}>
                {campaign.status}
              </div>
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
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl mb-4">Progress</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="stat">
                  <div className="stat-title">Artifacts Generated</div>
                  <div className="stat-value text-primary">{status.progress.artifacts_generated}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Revision Count</div>
                  <div className="stat-value text-secondary">{status.progress.revision_count}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Execution Time</div>
                  <div className="stat-value text-accent">{status.progress.execution_time?.toFixed(2)}s</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Download Section */}
        {campaign.status === 'completed' && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl mb-4">Download Results</h3>
              <div className="flex flex-wrap gap-4 mb-6">
                <button onClick={downloadWebsite} className="btn btn-primary">
                  📄 Download Website
                </button>
                <button onClick={downloadPDF} className="btn btn-secondary">
                  📊 Download PDF Report
                </button>
              </div>
              
              <div className="collapse collapse-arrow bg-base-200">
                <input type="checkbox" /> 
                <div className="collapse-title text-xl font-medium">
                  Generated Artifacts
                </div>
                <div className="collapse-content"> 
                  <pre className="bg-base-300 p-4 rounded-lg overflow-x-auto text-sm">
                    {JSON.stringify(campaign.artifacts, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Section */}
        {campaign.status === 'failed' && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="alert alert-error">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-bold">Campaign Generation Failed</h3>
                  <div className="text-xs">{campaign.message}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Running Status */}
        {campaign.status === 'running' && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="alert alert-info">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                  <h3 className="font-bold">Campaign in Progress</h3>
                  <div className="text-xs">
                    <p>Your campaign is being generated by our AI agents. This may take several minutes.</p>
                    <p className="mt-2"><strong>Status:</strong> {campaign.message}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 