import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export const CampaignGenerator = () => {
  const [brief, setBrief] = useState({
    campaign_name: '',
    target_audience: '',
    industry: '',
    campaign_goals: '',
    key_features: [''],
    tone: 'professional',
    budget_range: 'medium',
    timeline: '1-2 weeks'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiClient.generateCampaign(brief);
      navigate(`/campaign/${response.campaign_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate campaign');
    } finally {
      setLoading(false);
    }
  };

  const addFeature = () => {
    setBrief(prev => ({
      ...prev,
      key_features: [...prev.key_features, '']
    }));
  };

  const removeFeature = (index: number) => {
    setBrief(prev => ({
      ...prev,
      key_features: prev.key_features.filter((_, i) => i !== index)
    }));
  };

  const updateFeature = (index: number, value: string) => {
    setBrief(prev => ({
      ...prev,
      key_features: prev.key_features.map((feature, i) => i === index ? value : feature)
    }));
  };

  return (
    <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
      <div className="max-w-4xl mx-auto">
        <div className="card-mm">
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-mm-primary mb-4">
                <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-[var(--mm-gray-900)]">Campaign Generator</h1>
              <p className="text-[var(--mm-gray-600)]">
                Create a comprehensive marketing campaign using our advanced AI agents
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Campaign Name *</span>
                  </label>
                  <input
                    type="text"
                    placeholder="Enter campaign name"
                    className="input input-mm w-full"
                    value={brief.campaign_name}
                    onChange={(e) => setBrief(prev => ({ ...prev, campaign_name: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Target Audience *</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Young professionals, 25-35"
                    className="input input-mm w-full"
                    value={brief.target_audience}
                    onChange={(e) => setBrief(prev => ({ ...prev, target_audience: e.target.value }))}
                    required
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Industry *</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g., Technology, Healthcare, Finance"
                  className="input input-mm w-full"
                  value={brief.industry}
                  onChange={(e) => setBrief(prev => ({ ...prev, industry: e.target.value }))}
                  required
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Campaign Goals *</span>
                </label>
                <textarea
                  placeholder="Describe your campaign objectives and what you want to achieve"
                  className="textarea textarea-mm w-full h-24"
                  value={brief.campaign_goals}
                  onChange={(e) => setBrief(prev => ({ ...prev, campaign_goals: e.target.value }))}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Tone</span>
                  </label>
                  <select
                    className="select select-mm w-full"
                    value={brief.tone}
                    onChange={(e) => setBrief(prev => ({ ...prev, tone: e.target.value }))}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="creative">Creative</option>
                  </select>
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Budget Range</span>
                  </label>
                  <select
                    className="select select-mm w-full"
                    value={brief.budget_range}
                    onChange={(e) => setBrief(prev => ({ ...prev, budget_range: e.target.value }))}
                  >
                    <option value="low">Low ($1K - $5K)</option>
                    <option value="medium">Medium ($5K - $20K)</option>
                    <option value="high">High ($20K+)</option>
                  </select>
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Timeline</span>
                  </label>
                  <select
                    className="select select-mm w-full"
                    value={brief.timeline}
                    onChange={(e) => setBrief(prev => ({ ...prev, timeline: e.target.value }))}
                  >
                    <option value="1-2 weeks">1-2 weeks</option>
                    <option value="1 month">1 month</option>
                    <option value="2-3 months">2-3 months</option>
                    <option value="3+ months">3+ months</option>
                  </select>
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Key Features</span>
                </label>
                <div className="space-y-3">
                  {brief.key_features.map((feature, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        placeholder={`Feature ${index + 1}`}
                        className="input input-mm flex-1"
                        value={feature}
                        onChange={(e) => updateFeature(index, e.target.value)}
                      />
                      {brief.key_features.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeFeature(index)}
                          className="btn btn-circle btn-sm text-[var(--mm-error)] hover:bg-red-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addFeature}
                    className="btn btn-outline btn-sm text-mm-secondary border-mm-secondary hover:bg-mm-secondary-bg"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Feature
                  </button>
                </div>
              </div>

              <div className="form-control mt-6">
                <button
                  type="submit"
                  className={`btn btn-wide ${loading ? 'loading' : 'btn-mm-primary'}`}
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
            
            {error && (
              <div className="alert alert-error mt-6">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 