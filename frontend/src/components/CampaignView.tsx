import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';

export const CampaignView: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!campaignId) return;
    fetchCampaignWebsite();
  }, [campaignId]);

  const fetchCampaignWebsite = async () => {
    if (!campaignId) return;
    
    try {
      setLoading(true);
      setError(null);
      const content = await apiClient.viewCampaignWebsite(campaignId);
      setHtmlContent(content);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch campaign website');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <h3>Loading campaign website...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message">
          <h3>Error Loading Campaign Website</h3>
          <p>{error}</p>
          <div style={{ marginTop: '20px' }}>
            <button onClick={fetchCampaignWebsite} className="btn">
              Try Again
            </button>
            <Link to="/campaigns" className="btn btn-secondary" style={{ marginLeft: '10px' }}>
              Back to Campaigns
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!htmlContent) {
    return (
      <div className="container">
        <div className="error-message">
          <h3>No Content Available</h3>
          <p>The campaign website content could not be loaded.</p>
          <Link to="/campaigns" className="btn btn-secondary">
            Back to Campaigns
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="campaign-view">


      {/* Website Content */}
      <div style={{ 
        background: '#f8f9fa', 
        minHeight: 'calc(100vh - 100px)',
        padding: '20px'
      }}>
        <div style={{ 
          background: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '20px'
        }}>
          {/* Responsive iframe for the website */}
          <div style={{ 
            position: 'relative', 
            width: '100%', 
            minHeight: '600px',
            border: '1px solid #dee2e6'
          }}>
            <iframe
              srcDoc={htmlContent}
              title={`Campaign Website - ${campaignId}`}
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
                minHeight: '600px'
              }}
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
            />
          </div>
        </div>
      </div>

      {/* Footer with additional actions */}
      <div style={{ 
        background: 'white', 
        padding: '20px', 
        borderTop: '1px solid #dee2e6',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <p style={{ color: '#666', margin: '0 0 15px 0' }}>
            This is a preview of your generated campaign website
          </p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <Link 
              to={`/campaign/${campaignId}`} 
              className="btn"
            >
              Download Files
            </Link>
            <Link 
              to="/campaigns" 
              className="btn btn-secondary"
            >
              View All Campaigns
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
