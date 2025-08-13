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
        return '#28a745';
      case 'running':
        return '#ffc107';
      case 'failed':
        return '#dc3545';
      case 'initialized':
        return '#17a2b8';
      default:
        return '#6c757d';
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
      <div className="container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <h3>Loading campaigns...</h3>
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
          <button onClick={fetchCampaigns} className="btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!campaigns || campaigns.campaigns.length === 0) {
    return (
      <div className="container">
        <div className="form-container">
          <h2>No Campaigns Found</h2>
          <p>You haven't created any campaigns yet.</p>
          <Link to="/generate" className="btn">
            Create Your First Campaign
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="campaign-list">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <h2>Your Campaigns</h2>
          <Link to="/generate" className="btn">
            Create New Campaign
          </Link>
        </div>

        {/* Summary Cards */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '20px', 
          marginBottom: '30px' 
        }}>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#28a745', margin: '0 0 10px 0' }}>{campaigns.total}</h3>
            <p style={{ margin: 0, color: '#666' }}>Total Campaigns</p>
          </div>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#28a745', margin: '0 0 10px 0' }}>{campaigns.completed}</h3>
            <p style={{ margin: 0, color: '#666' }}>Completed</p>
          </div>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#ffc107', margin: '0 0 10px 0' }}>{campaigns.running}</h3>
            <p style={{ margin: 0, color: '#666' }}>Running</p>
          </div>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#dc3545', margin: '0 0 10px 0' }}>{campaigns.failed}</h3>
            <p style={{ margin: 0, color: '#666' }}>Failed</p>
          </div>
        </div>

        {/* Campaigns Table */}
        <div style={{ 
          background: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8f9fa' }}>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Campaign ID</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Status</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Created</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Execution Time</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Artifacts</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.campaigns.map((campaign) => (
                <tr key={campaign.campaign_id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '15px', fontFamily: 'monospace', fontSize: '12px' }}>
                    {campaign.campaign_id}
                  </td>
                  <td style={{ padding: '15px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: 'white',
                      backgroundColor: getStatusColor(campaign.status)
                    }}>
                      {campaign.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>
                    {formatDate(campaign.created_at)}
                  </td>
                  <td style={{ padding: '15px' }}>
                    {campaign.execution_time 
                      ? `${campaign.execution_time.toFixed(2)}s`
                      : '-'
                    }
                  </td>
                  <td style={{ padding: '15px' }}>
                    {campaign.artifacts_count}
                  </td>
                  <td style={{ padding: '15px' }}>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <Link 
                        to={`/campaign/${campaign.campaign_id}`}
                        className="btn"
                        style={{ padding: '8px 12px', fontSize: '12px' }}
                      >
                        View
                      </Link>
                      {campaign.status === 'completed' && (
                        <Link 
                          to={`/campaign/view/${campaign.campaign_id}`}
                          className="btn btn-primary"
                          style={{ padding: '8px 12px', fontSize: '12px' }}
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

        {/* Refresh Button */}
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button onClick={fetchCampaigns} className="btn btn-secondary">
            Refresh Campaigns
          </button>
        </div>
      </div>
    </div>
  );
};
