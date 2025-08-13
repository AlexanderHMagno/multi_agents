import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CampaignBrief } from '../types';

export const CampaignGenerator = () => {
  const [brief, setBrief] = useState<CampaignBrief>({
    product: '',
    client: '',
    target_audience: '',
    goals: [''],
    key_features: [''],
    color_scheme: 'professional',
    budget: '$5,000',
    timeline: '3 months'
  });
  const [loading, setLoading] = useState(false);
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateCampaign(brief);
      setCampaignId(response.campaign_id);
      alert('Campaign generation started! Use the campaign ID to monitor progress.');
    } catch (err: any) {
      setError(err.detail || 'Failed to generate campaign. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const addGoal = () => {
    setBrief(prev => ({ ...prev, goals: [...prev.goals, ''] }));
  };

  const addFeature = () => {
    setBrief(prev => ({ ...prev, key_features: [...prev.key_features, ''] }));
  };

  const updateGoal = (index: number, value: string) => {
    setBrief(prev => ({
      ...prev,
      goals: prev.goals.map((goal, i) => i === index ? value : goal)
    }));
  };

  const updateFeature = (index: number, value: string) => {
    setBrief(prev => ({
      ...prev,
      key_features: prev.key_features.map((feature, i) => i === index ? value : feature)
    }));
  };

  const removeGoal = (index: number) => {
    if (brief.goals.length > 1) {
      setBrief(prev => ({
        ...prev,
        goals: prev.goals.filter((_, i) => i !== index)
      }));
    }
  };

  const removeFeature = (index: number) => {
    if (brief.key_features.length > 1) {
      setBrief(prev => ({
        ...prev,
        key_features: prev.key_features.filter((_, i) => i !== index)
      }));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setBrief(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="container">
      <div className="form-container">
        <h2>🚀 Generate New Campaign</h2>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {campaignId && (
          <div className="success-message">
            <h3>Campaign Started!</h3>
            <p><strong>Campaign ID:</strong> {campaignId}</p>
            <p>Check the campaign status to monitor progress and download results.</p>
            <button 
              onClick={() => navigate(`/campaign/${campaignId}`)} 
              className="btn"
            >
              Monitor Campaign
            </button>
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="product">Product/Service:</label>
            <input
              id="product"
              type="text"
              name="product"
              value={brief.product}
              onChange={handleChange}
              required
              placeholder="e.g., Eco-Friendly Water Bottle"
            />
          </div>

          <div className="form-group">
            <label htmlFor="client">Client Company:</label>
            <input
              id="client"
              type="text"
              name="client"
              value={brief.client}
              onChange={handleChange}
              required
              placeholder="e.g., GreenLife Inc"
            />
          </div>

          <div className="form-group">
            <label htmlFor="client_website">Client Website (optional):</label>
            <input
              id="client_website"
              type="url"
              name="client_website"
              value={brief.client_website || ''}
              onChange={handleChange}
              placeholder="https://example.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="client_logo">Client Logo URL (optional):</label>
            <input
              id="client_logo"
              type="url"
              name="client_logo"
              value={brief.client_logo || ''}
              onChange={handleChange}
              placeholder="https://example.com/logo.png"
            />
          </div>

          <div className="form-group">
            <label htmlFor="target_audience">Target Audience:</label>
            <textarea
              id="target_audience"
              name="target_audience"
              value={brief.target_audience}
              onChange={handleChange}
              required
              placeholder="Describe your target audience in detail"
            />
          </div>

          <div className="form-group">
            <label>Campaign Goals:</label>
            {brief.goals.map((goal, index) => (
              <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input
                  type="text"
                  value={goal}
                  onChange={(e) => updateGoal(index, e.target.value)}
                  placeholder="Enter campaign goal"
                  required
                  style={{ flex: 1 }}
                />
                {brief.goals.length > 1 && (
                  <button 
                    type="button" 
                    onClick={() => removeGoal(index)}
                    className="btn btn-secondary"
                    style={{ padding: '10px 15px' }}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button type="button" onClick={addGoal} className="btn btn-secondary">
              Add Goal
            </button>
          </div>

          <div className="form-group">
            <label>Key Features:</label>
            {brief.key_features.map((feature, index) => (
              <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input
                  type="text"
                  value={feature}
                  onChange={(e) => updateFeature(index, e.target.value)}
                  placeholder="Enter key feature"
                  required
                  style={{ flex: 1 }}
                />
                {brief.key_features.length > 1 && (
                  <button 
                    type="button" 
                    onClick={() => removeFeature(index)}
                    className="btn btn-secondary"
                    style={{ padding: '10px 15px' }}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button type="button" onClick={addFeature} className="btn btn-secondary">
              Add Feature
            </button>
          </div>

          <div className="form-group">
            <label htmlFor="color_scheme">Color Scheme:</label>
            <select
              id="color_scheme"
              name="color_scheme"
              value={brief.color_scheme}
              onChange={handleChange}
            >
              <option value="professional">Professional</option>
              <option value="creative">Creative</option>
              <option value="modern">Modern</option>
              <option value="vintage">Vintage</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="budget">Budget:</label>
            <input
              id="budget"
              type="text"
              name="budget"
              value={brief.budget}
              onChange={handleChange}
              placeholder="$5,000"
            />
          </div>

          <div className="form-group">
            <label htmlFor="timeline">Timeline:</label>
            <input
              id="timeline"
              type="text"
              name="timeline"
              value={brief.timeline}
              onChange={handleChange}
              placeholder="3 months"
            />
          </div>

          <div className="form-group">
            <label htmlFor="additional_requirements">Additional Requirements:</label>
            <textarea
              id="additional_requirements"
              name="additional_requirements"
              value={brief.additional_requirements || ''}
              onChange={handleChange}
              placeholder="Any additional requirements or notes..."
            />
          </div>

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Generating Campaign...' : 'Generate Campaign'}
          </button>
        </form>
      </div>
    </div>
  );
}; 