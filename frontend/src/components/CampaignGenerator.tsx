import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

// Predefined campaign goals for quick selection
const commonCampaignGoals = [
  'Increase brand awareness',
  'Generate leads and conversions',
  'Launch new product/service',
  'Improve customer engagement',
  'Drive website traffic',
  'Boost social media presence',
  'Increase sales revenue',
  'Build customer loyalty',
  'Enter new markets',
  'Reposition brand image',
  'Promote seasonal offers',
  'Educate target audience',
  'Support event marketing',
  'Crisis management',
  'Competitive positioning'
];

// Predefined key features for quick selection
const commonFeatures = [
  'User-friendly interface',
  'Mobile responsive design',
  'Fast loading speed',
  'SEO optimization',
  'Social media integration',
  'Analytics and tracking',
  'Customer support system',
  'Payment processing',
  'Multi-language support',
  'Accessibility features',
  'Security measures',
  'Cloud-based solution',
  'API integration',
  'Custom branding',
  'Performance optimization',
  'Content management system',
  'Email marketing tools',
  'Lead generation forms',
  'Customer testimonials',
  'Product showcase'
];

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
  const [showGoalsModal, setShowGoalsModal] = useState(false);
  const [showFeaturesModal, setShowFeaturesModal] = useState(false);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
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

  const handleGoalSelection = (goal: string) => {
    if (selectedGoals.includes(goal)) {
      setSelectedGoals(prev => prev.filter(g => g !== goal));
    } else {
      setSelectedGoals(prev => [...prev, goal]);
    }
  };

  const handleFeatureSelection = (feature: string) => {
    if (selectedFeatures.includes(feature)) {
      setSelectedFeatures(prev => prev.filter(f => f !== feature));
    } else {
      setSelectedFeatures(prev => [...prev, feature]);
    }
  };

  const applySelectedGoals = () => {
    const goalsText = selectedGoals.join('. ');
    setBrief(prev => ({ ...prev, campaign_goals: goalsText }));
    setShowGoalsModal(false);
  };

  const applySelectedFeatures = () => {
    const featuresList = selectedFeatures.length > 0 ? selectedFeatures : brief.key_features.filter(f => f.trim() !== '');
    setBrief(prev => ({ ...prev, key_features: featuresList }));
    setShowFeaturesModal(false);
  };

  const addCustomGoal = (customGoal: string) => {
    if (customGoal.trim() && !selectedGoals.includes(customGoal.trim())) {
      setSelectedGoals(prev => [...prev, customGoal.trim()]);
    }
  };

  const addCustomFeature = (customFeature: string) => {
    if (customFeature.trim() && !selectedFeatures.includes(customFeature.trim())) {
      setSelectedFeatures(prev => [...prev, customFeature.trim()]);
    }
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
                  <button
                    type="button"
                    onClick={() => setShowGoalsModal(true)}
                    className="btn btn-sm btn-mm-secondary ml-2"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Quick Select
                  </button>
                </label>
                <textarea
                  placeholder="Describe your campaign objectives and what you want to achieve"
                  className="textarea textarea-mm w-full h-24"
                  value={brief.campaign_goals}
                  onChange={(e) => setBrief(prev => ({ ...prev, campaign_goals: e.target.value }))}
                  required
                />
                {brief.campaign_goals && (
                  <div className="mt-2">
                    <label className="label">
                      <span className="label-text text-sm text-[var(--mm-gray-500)]">Selected Goals:</span>
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {brief.campaign_goals.split('.').filter(goal => goal.trim()).map((goal, index) => (
                        <span key={index} className="badge badge-mm-primary">
                          {goal.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
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
                  <button
                    type="button"
                    onClick={() => setShowFeaturesModal(true)}
                    className="btn btn-sm btn-mm-secondary ml-2"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Quick Select
                  </button>
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
                {brief.key_features.filter(f => f.trim()).length > 0 && (
                  <div className="mt-2">
                    <label className="label">
                      <span className="label-text text-sm text-[var(--mm-gray-500)]">Selected Features:</span>
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {brief.key_features.filter(f => f.trim()).map((feature, index) => (
                        <span key={index} className="badge badge-mm-secondary">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
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

      {/* Campaign Goals Modal */}
      {showGoalsModal && (
        <div className="modal modal-open">
          <div className="modal-box max-w-4xl">
            <h3 className="font-bold text-lg text-[var(--mm-gray-900)] mb-4">Select Campaign Goals</h3>
            <div className="mb-4">
              <label className="label">
                <span className="label-text font-medium text-[var(--mm-gray-700)]">Add Custom Goal:</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter custom goal"
                  className="input input-mm flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addCustomGoal((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Enter custom goal"]') as HTMLInputElement;
                    if (input) {
                      addCustomGoal(input.value);
                      input.value = '';
                    }
                  }}
                  className="btn btn-mm-primary"
                >
                  Add
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {commonCampaignGoals.map((goal) => (
                <label key={goal} className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-[var(--mm-gray-100)]">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-mm-primary"
                    checked={selectedGoals.includes(goal)}
                    onChange={() => handleGoalSelection(goal)}
                  />
                  <span className="text-[var(--mm-gray-700)]">{goal}</span>
                </label>
              ))}
            </div>
            <div className="modal-action">
              <button
                type="button"
                className="btn btn-mm-secondary"
                onClick={() => setShowGoalsModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-mm-primary"
                onClick={applySelectedGoals}
              >
                Apply Selected Goals
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Key Features Modal */}
      {showFeaturesModal && (
        <div className="modal modal-open">
          <div className="modal-box max-w-4xl">
            <h3 className="font-bold text-lg text-[var(--mm-gray-900)] mb-4">Select Key Features</h3>
            <div className="mb-4">
              <label className="label">
                <span className="label-text font-medium text-[var(--mm-gray-700)]">Add Custom Feature:</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter custom feature"
                  className="input input-mm flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addCustomFeature((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Enter custom feature"]') as HTMLInputElement;
                    if (input) {
                      addCustomFeature(input.value);
                      input.value = '';
                    }
                  }}
                  className="btn btn-mm-primary"
                >
                  Add
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {commonFeatures.map((feature) => (
                <label key={feature} className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-[var(--mm-gray-100)]">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-mm-primary"
                    checked={selectedFeatures.includes(feature)}
                    onChange={() => handleFeatureSelection(feature)}
                  />
                  <span className="text-[var(--mm-gray-700)]">{feature}</span>
                </label>
              ))}
            </div>
            <div className="modal-action">
              <button
                type="button"
                className="btn btn-mm-secondary"
                onClick={() => setShowFeaturesModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-mm-primary"
                onClick={applySelectedFeatures}
              >
                Apply Selected Features
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 