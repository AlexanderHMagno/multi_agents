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
      <div className="container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <h3>Loading campaign...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="container">
        <div className="error-message">
          <h3>Campaign Not Found</h3>
          <p>The requested campaign could not be found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="campaign-monitor">
        <h2>Campaign Status: {campaign.status}</h2>
        
        <div className="campaign-info">
          <p><strong>Campaign ID:</strong> {campaign.campaign_id}</p>
          <p><strong>Created:</strong> {new Date(campaign.created_at).toLocaleString()}</p>
          <p><strong>Created By:</strong> {campaign.created_by}</p>
          {campaign.execution_time && (
            <p><strong>Execution Time:</strong> {campaign.execution_time.toFixed(2)} seconds</p>
          )}
          {campaign.quality_score && (
            <p><strong>Quality Score:</strong> {campaign.quality_score}</p>
          )}
          {campaign.revision_count && (
            <p><strong>Revisions:</strong> {campaign.revision_count}</p>
          )}
        </div>

        {status?.progress && (
          <div className="progress-info">
            <h3>Progress</h3>
            <p>Artifacts Generated: {status.progress.artifacts_generated}</p>
            <p>Revision Count: {status.progress.revision_count}</p>
            <p>Execution Time: {status.progress.execution_time?.toFixed(2)} seconds</p>
          </div>
        )}

        {campaign.status === 'completed' && (
          <div className="download-section">
            <h3>Download Results</h3>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
              <button onClick={downloadWebsite} className="btn">
                Download Website
              </button>
              <button onClick={downloadPDF} className="btn">
                Download PDF Report
              </button>
            </div>
            
            <div className="artifacts">
              <h4>Generated Artifacts:</h4>
              <pre>{JSON.stringify(campaign.artifacts, null, 2)}</pre>
            </div>
          </div>
        )}

        {campaign.status === 'failed' && (
          <div className="error-section">
            <h3>Campaign Generation Failed</h3>
            <p>{campaign.message}</p>
          </div>
        )}

        {campaign.status === 'running' && (
          <div className="progress-info">
            <h3>Campaign in Progress</h3>
            <p>Your campaign is being generated by our AI agents. This may take several minutes.</p>
            <p>Status: {campaign.message}</p>
          </div>
        )}
      </div>
    </div>
  );
}; 