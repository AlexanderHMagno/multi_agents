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

// Predefined target audience ideas for quick selection
const commonTargetAudiences = [
  'Young professionals (25-35)',
  'Small business owners',
  'Enterprise decision makers',
  'Tech-savvy millennials',
  'Baby boomers (55+)',
  'Working parents',
  'Students and recent graduates',
  'Remote workers',
  'Urban professionals',
  'Suburban families',
  'Creative professionals',
  'Healthcare professionals',
  'Financial services clients',
  'E-commerce shoppers',
  'B2B decision makers',
  'Startup founders',
  'Non-profit organizations',
  'Government agencies',
  'Educational institutions',
  'Healthcare organizations'
];

// Predefined key features for marketing campaigns
const commonFeatures = [
  'Social media integration',
  'Email marketing automation',
  'Lead generation forms',
  'Analytics and tracking',
  'A/B testing capabilities',
  'Customer segmentation',
  'Personalized messaging',
  'Multi-channel campaigns',
  'Retargeting strategies',
  'Influencer partnerships',
  'Content marketing tools',
  'SEO optimization',
  'PPC campaign management',
  'Marketing automation',
  'CRM integration',
  'Customer journey mapping',
  'Conversion rate optimization',
  'Mobile-first design',
  'Video marketing tools',
  'Interactive content features',
  'Social proof elements',
  'Urgency and scarcity tactics',
  'Referral programs',
  'Loyalty programs',
  'Gamification elements'
];

export const CampaignGenerator = () => {
  const [brief, setBrief] = useState({
    campaign_name: '',
    product: '',
    client: '',
    client_website: '',
    client_logo: '',
    color_scheme: 'professional',
    target_audience: '',
    goals: [''],
    key_features: [''],
    budget: '$5,000',
    timeline: '3 months',
    additional_requirements: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGoalsModal, setShowGoalsModal] = useState(false);
  const [showFeaturesModal, setShowFeaturesModal] = useState(false);
  const [showAudienceModal, setShowAudienceModal] = useState(false);
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
  const [selectedAudience, setSelectedAudience] = useState<string[]>([]);
  const [jsonInput, setJsonInput] = useState('');
  const [jsonError, setJsonError] = useState('');
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

  const handleAudienceSelection = (audience: string) => {
    if (selectedAudience.includes(audience)) {
      setSelectedAudience(prev => prev.filter(a => a !== audience));
    } else {
      setSelectedAudience(prev => [...prev, audience]);
    }
  };

  const applySelectedGoals = () => {
    const goalsList = selectedGoals.length > 0 ? selectedGoals : brief.goals.filter(g => g.trim() !== '');
    setBrief(prev => ({ ...prev, goals: goalsList }));
    setShowGoalsModal(false);
  };

  const applySelectedFeatures = () => {
    const featuresList = selectedFeatures.length > 0 ? selectedFeatures : brief.key_features.filter(f => f.trim() !== '');
    setBrief(prev => ({ ...prev, key_features: featuresList }));
    setShowFeaturesModal(false);
  };

  const applySelectedAudience = () => {
    const audienceText = selectedAudience.length > 0 ? selectedAudience.join(', ') : brief.target_audience;
    setBrief(prev => ({ ...prev, target_audience: audienceText }));
    setShowAudienceModal(false);
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

  const addCustomAudience = (customAudience: string) => {
    if (customAudience.trim() && !selectedAudience.includes(customAudience.trim())) {
      setSelectedAudience(prev => [...prev, customAudience.trim()]);
    }
  };

  const importFromJson = () => {
    try {
      setJsonError('');
      const parsedData = JSON.parse(jsonInput);
      
      // Validate required fields
      if (!parsedData.product || !parsedData.client || !parsedData.target_audience) {
        setJsonError('Missing required fields: product, client, and target_audience are required');
        return;
      }

      // Update the form with imported data
      setBrief({
        campaign_name: parsedData.campaign_name || '',
        product: parsedData.product || '',
        client: parsedData.client || '',
        client_website: parsedData.client_website || '',
        client_logo: parsedData.client_logo || '',
        color_scheme: parsedData.color_scheme || 'professional',
        target_audience: parsedData.target_audience || '',
        goals: Array.isArray(parsedData.goals) && parsedData.goals.length > 0 
          ? parsedData.goals 
          : [''],
        key_features: Array.isArray(parsedData.key_features) && parsedData.key_features.length > 0 
          ? parsedData.key_features 
          : [''],
        budget: parsedData.budget || '$5,000',
        timeline: parsedData.timeline || '3 months',
        additional_requirements: parsedData.additional_requirements || ''
      });

      // Update selected arrays for modals
      if (Array.isArray(parsedData.goals)) {
        setSelectedGoals(parsedData.goals);
      }
      if (Array.isArray(parsedData.key_features)) {
        setSelectedFeatures(parsedData.key_features);
      }
      if (parsedData.target_audience) {
        setSelectedAudience([parsedData.target_audience]);
      }

      // Close modal and show success
      setShowJsonModal(false);
      setJsonInput('');
      
      // Show success message (you can add a toast notification here)
      console.log('Campaign data imported successfully from JSON');
      
    } catch (error) {
      setJsonError('Invalid JSON format. Please check your JSON syntax.');
      console.error('JSON import error:', error);
    }
  };

  const loadSampleJson = () => {
    const sampleJson = {
      "product": "Cit-E Cycles e-Bikes – featured Moustache Dimanche 29 Gravel 2 EQ & 4 EQ",
      "client": "Cit-E Cycles",
      "client_website": "https://www.citecycles.com/",
      "client_logo": "[to be provided by client]",
      "color_scheme": "professional",
      "target_audience": "Outdoor enthusiasts and urban commuters in British Columbia seeking high-quality, electric-powered cycling solutions",
      "goals": [
        "Raise awareness of Cit-E Cycles as Canada's premier e-bike retailer",
        "Promote the 2025 Moustache Dimanche 29 Gravel line (2 EQ & 4 EQ)",
        "Drive foot traffic and test rides at BC showroom locations",
        "Establish Cit-E Cycles as a trusted expert in e-bike service and support"
      ],
      "key_features": [
        "Extensive e-bike selection—20+ brands, 300+ models",
        "Top-tier Gravel models priced at CA$5,899 and CA$7,499",
        "Exceptional customer service backed by 100+ years of experience",
        "Multiple convenient locations across BC"
      ],
      "budget": "$5,000",
      "timeline": "3 months",
      "additional_requirements": "In-store test-ride events; QR codes linking to booking page; highlight accessible service and financing options"
    };
    
    setJsonInput(JSON.stringify(sampleJson, null, 2));
  };

  return (
    <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
      <div className="max-w-4xl mx-auto">
        <div className="card-mm">
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-mm-primary mb-4">
                <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-[var(--mm-gray-900)]">Campaign Generator</h1>
              <p className="text-[var(--mm-gray-600)] mb-4">
                Create a comprehensive marketing campaign using our advanced AI agents
              </p>
              <button
                type="button"
                onClick={() => setShowJsonModal(true)}
                className="btn btn-mm-secondary btn-sm"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                </svg>
                Import from JSON
              </button>
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
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Product/Service *</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Eco-Friendly Water Bottle"
                    className="input input-mm w-full"
                    value={brief.product}
                    onChange={(e) => setBrief(prev => ({ ...prev, product: e.target.value }))}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Client Company *</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., GreenLife Inc"
                    className="input input-mm w-full"
                    value={brief.client}
                    onChange={(e) => setBrief(prev => ({ ...prev, client: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Target Audience *</span>
                    <button
                      type="button"
                      onClick={() => setShowAudienceModal(true)}
                      className="btn btn-sm btn-mm-secondary ml-2"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Pick Ideas
                    </button>
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Client Website (Optional)</span>
                  </label>
                  <input
                    type="url"
                    placeholder="https://example.com"
                    className="input input-mm w-full"
                    value={brief.client_website}
                    onChange={(e) => setBrief(prev => ({ ...prev, client_website: e.target.value }))}
                  />
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Client Logo URL (Optional)</span>
                  </label>
                  <input
                    type="url"
                    placeholder="https://example.com/logo.png"
                    className="input input-mm w-full"
                    value={brief.client_logo}
                    onChange={(e) => setBrief(prev => ({ ...prev, client_logo: e.target.value }))}
                  />
                </div>
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
                <div className="space-y-3">
                  {brief.goals.map((goal, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        placeholder={`Goal ${index + 1}`}
                        className="input input-mm flex-1"
                        value={goal}
                        onChange={(e) => updateGoal(index, e.target.value)}
                        required
                      />
                      {brief.goals.length > 1 && (
                        <button
                          type="button"
                          onClick={() => {
                            setBrief(prev => ({
                              ...prev,
                              goals: prev.goals.filter((_, i) => i !== index)
                            }));
                          }}
                          className="btn btn-circle btn-sm text-[var(--mm-error)] hover:bg-red-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
          
                </div>
                {brief.goals.filter(g => g.trim()).length > 0 && (
                  <div className="mt-2">
                    <label className="label">
                      <span className="label-text text-sm text-[var(--mm-gray-500)]">Selected Goals:</span>
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {brief.goals.filter(g => g.trim()).map((goal, index) => (
                        <span key={index} className="badge badge-mm-primary">
                          {goal}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Key Features *</span>
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
                        required
                      />
                      {brief.key_features.length > 1 && (
                        <button
                          type="button"
                          onClick={() => {
                            setBrief(prev => ({
                              ...prev,
                              key_features: prev.key_features.filter((_, i) => i !== index)
                            }));
                          }}
                          className="btn btn-circle btn-sm text-[var(--mm-error)] hover:bg-red-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
          
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

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Color Scheme</span>
                  </label>
                  <select
                    className="select select-mm w-full"
                    value={brief.color_scheme}
                    onChange={(e) => setBrief(prev => ({ ...prev, color_scheme: e.target.value }))}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="creative">Creative</option>
                    <option value="modern">Modern</option>
                    <option value="vintage">Vintage</option>
                  </select>
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Budget</span>
                  </label>
                  <input
                    type="text"
                    placeholder="$5,000"
                    className="input input-mm w-full"
                    value={brief.budget}
                    onChange={(e) => setBrief(prev => ({ ...prev, budget: e.target.value }))}
                  />
                </div>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium text-[var(--mm-gray-700)]">Timeline</span>
                  </label>
                  <input
                    type="text"
                    placeholder="3 months"
                    className="input input-mm w-full"
                    value={brief.timeline}
                    onChange={(e) => setBrief(prev => ({ ...prev, timeline: e.target.value }))}
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Additional Requirements</span>
                </label>
                <textarea
                  placeholder="Any additional requirements or notes..."
                  className="textarea textarea-mm w-full h-24"
                  value={brief.additional_requirements}
                  onChange={(e) => setBrief(prev => ({ ...prev, additional_requirements: e.target.value }))}
                />
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

      {/* Target Audience Modal */}
      {showAudienceModal && (
        <div className="modal modal-open">
          <div className="modal-box max-w-4xl">
            <h3 className="font-bold text-lg text-[var(--mm-gray-900)] mb-4">Select Target Audience</h3>
            <div className="mb-4">
              <label className="label">
                <span className="label-text font-medium text-[var(--mm-gray-700)]">Add Custom Audience:</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter custom audience"
                  className="input input-mm flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addCustomAudience((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Enter custom audience"]') as HTMLInputElement;
                    if (input) {
                      addCustomAudience(input.value);
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
              {commonTargetAudiences.map((audience) => (
                <label key={audience} className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-[var(--mm-gray-100)]">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-mm-primary"
                    checked={selectedAudience.includes(audience)}
                    onChange={() => handleAudienceSelection(audience)}
                  />
                  <span className="text-[var(--mm-gray-700)]">{audience}</span>
                </label>
              ))}
            </div>
            <div className="modal-action">
              <button
                type="button"
                className="btn btn-mm-secondary"
                onClick={() => setShowAudienceModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-mm-primary"
                onClick={applySelectedAudience}
              >
                Apply Selected Audience
              </button>
            </div>
          </div>
        </div>
      )}

      {/* JSON Import Modal */}
      {showJsonModal && (
        <div className="modal modal-open">
          <div className="modal-box max-w-6xl">
            <h3 className="font-bold text-lg text-[var(--mm-gray-900)] mb-4">Import Campaign from JSON</h3>
            
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <label className="label">
                  <span className="label-text font-medium text-[var(--mm-gray-700)]">Paste your JSON campaign data:</span>
                </label>
                <button
                  type="button"
                  onClick={loadSampleJson}
                  className="btn btn-sm btn-mm-secondary"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Load Sample
                </button>
              </div>
              <textarea
                className="textarea textarea-mm w-full h-96 font-mono text-sm"
                placeholder="Paste your JSON campaign data here..."
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
              />
              {jsonError && (
                <div className="alert alert-error mt-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{jsonError}</span>
                </div>
              )}
            </div>

            <div className="mb-4">
              <div className="alert alert-info">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h4 className="font-bold">JSON Format Requirements:</h4>
                  <ul className="text-sm mt-1">
                    <li><strong>Required fields:</strong> product, client, target_audience</li>
                    <li><strong>Optional fields:</strong> campaign_name, client_website, client_logo, color_scheme, goals, key_features, budget, timeline, additional_requirements</li>
                    <li><strong>Arrays:</strong> goals and key_features should be arrays of strings</li>
                    <li><strong>Format:</strong> Valid JSON with proper quotes and commas</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="modal-action">
              <button
                type="button"
                className="btn btn-mm-secondary"
                onClick={() => {
                  setShowJsonModal(false);
                  setJsonInput('');
                  setJsonError('');
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-mm-primary"
                onClick={importFromJson}
                disabled={!jsonInput.trim()}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Import Campaign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 