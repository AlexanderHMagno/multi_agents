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
    <div className="min-h-screen bg-base-200 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="text-center mb-6">
              <div className="text-primary mb-4">
                <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-primary">Campaign Generator</h1>
              <p className="text-base-content/70">
                Create a comprehensive marketing campaign using our advanced AI agents
              </p>
            </div>
            
            {error && (
              <div className="alert alert-error mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            {campaignId && (
              <div className="alert alert-success mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-bold">Campaign Started!</h3>
                  <div className="text-xs">
                    <p><strong>Campaign ID:</strong> {campaignId}</p>
                    <p>Check the campaign status to monitor progress and download results.</p>
                  </div>
                </div>
                <button 
                  onClick={() => navigate(`/campaign/${campaignId}`)} 
                  className="btn btn-sm btn-primary"
                >
                  Monitor Campaign
                </button>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Product/Service *</span>
                  </label>
                  <input
                    type="text"
                    name="product"
                    value={brief.product}
                    onChange={handleChange}
                    required
                    placeholder="e.g., Eco-Friendly Water Bottle"
                    className="input input-bordered w-full"
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Client Company *</span>
                  </label>
                  <input
                    type="text"
                    name="client"
                    value={brief.client}
                    onChange={handleChange}
                    required
                    placeholder="e.g., GreenLife Inc"
                    className="input input-bordered w-full"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Client Website (optional)</span>
                  </label>
                  <input
                    type="url"
                    name="client_website"
                    value={brief.client_website || ''}
                    onChange={handleChange}
                    placeholder="https://example.com"
                    className="input input-bordered w-full"
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Client Logo URL (optional)</span>
                  </label>
                  <input
                    type="url"
                    name="client_logo"
                    value={brief.client_logo || ''}
                    onChange={handleChange}
                    placeholder="https://example.com/logo.png"
                    className="input input-bordered w-full"
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Target Audience *</span>
                </label>
                <textarea
                  name="target_audience"
                  value={brief.target_audience}
                  onChange={handleChange}
                  required
                  placeholder="Describe your target audience in detail"
                  className="textarea textarea-bordered w-full h-24"
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Campaign Goals *</span>
                </label>
                <div className="space-y-3">
                  {brief.goals.map((goal, index) => (
                    <div key={index} className="flex gap-3 items-center">
                      <input
                        type="text"
                        value={goal}
                        onChange={(e) => updateGoal(index, e.target.value)}
                        placeholder="Enter campaign goal"
                        required
                        className="input input-bordered flex-1"
                      />
                      {brief.goals.length > 1 && (
                        <button 
                          type="button" 
                          onClick={() => removeGoal(index)}
                          className="btn btn-error btn-sm"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                  <button type="button" onClick={addGoal} className="btn btn-secondary btn-sm">
                    + Add Goal
                  </button>
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Key Features *</span>
                </label>
                <div className="space-y-3">
                  {brief.key_features.map((feature, index) => (
                    <div key={index} className="flex gap-3 items-center">
                      <input
                        type="text"
                        value={feature}
                        onChange={(e) => updateFeature(index, e.target.value)}
                        placeholder="Enter key feature"
                        required
                        className="input input-bordered flex-1"
                      />
                      {brief.key_features.length > 1 && (
                        <button 
                          type="button" 
                          onClick={() => removeFeature(index)}
                          className="btn btn-error btn-sm"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                  <button type="button" onClick={addFeature} className="btn btn-secondary btn-sm">
                    + Add Feature
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Color Scheme</span>
                  </label>
                  <select
                    name="color_scheme"
                    value={brief.color_scheme}
                    onChange={handleChange}
                    className="select select-bordered w-full"
                  >
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                    <option value="modern">Modern</option>
                    <option value="vintage">Vintage</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Budget</span>
                  </label>
                  <input
                    type="text"
                    name="budget"
                    value={brief.budget}
                    onChange={handleChange}
                    placeholder="$5,000"
                    className="input input-bordered w-full"
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Timeline</span>
                  </label>
                  <input
                    type="text"
                    name="timeline"
                    value={brief.timeline}
                    onChange={handleChange}
                    placeholder="3 months"
                    className="input input-bordered w-full"
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Additional Requirements</span>
                </label>
                <textarea
                  name="additional_requirements"
                  value={brief.additional_requirements || ''}
                  onChange={handleChange}
                  placeholder="Any additional requirements or notes..."
                  className="textarea textarea-bordered w-full h-24"
                />
              </div>

              <div className="form-control mt-6">
                <button
                  type="submit"
                  className={`btn btn-primary btn-wide ${loading ? 'loading' : ''}`}
                  disabled={loading}
                >
                  {loading ? (
                    'Generating Campaign...'
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Generate Campaign
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}; 