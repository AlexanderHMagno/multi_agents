import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';

interface AgentInteraction {
  timestamp: string;
  agent: string;
  action: string;
  message: string;
  status: 'success' | 'error' | 'running';
}

interface CampaignProgress {
  current_step: string;
  step_name: string;
  step_description: string;
  total_steps: number;
  completed_steps: number;
  current_agent: string;
  last_update: string;
}

interface RealTimeProgress {
  campaign_id: string;
  status: string;
  progress: CampaignProgress;
  agent_interactions: AgentInteraction[];
  artifacts_count: number;
  revision_count: number;
  execution_time: number;
  last_update: string;
}

export const CampaignMonitor = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const [progress, setProgress] = useState<RealTimeProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (campaignId) {
      fetchProgress();
      // Real-time updates every 2 seconds
      const interval = setInterval(fetchProgress, 10000);
      return () => clearInterval(interval);
    }
  }, [campaignId]);

  const fetchProgress = async () => {
    try {
      const data = await apiClient.getCampaignProgress(campaignId!);
      setProgress(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch campaign progress');
    } finally {
      setLoading(false);
    }
  };

  const downloadWebsite = async () => {
    try {
      const blob = await apiClient.downloadWebsite(campaignId!);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${progress?.campaign_id}.html`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download website');
    }
  };

  const downloadPDF = async () => {
    try {
      const blob = await apiClient.downloadPDF(campaignId!);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${progress?.campaign_id}_report.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    }
  };

  const getStepIcon = (step: string) => {
    const icons = {
      initializing: '🔄',
      analyzing_brief: '📋',
      content_generation: '✍️',
      design_creation: '🎨',
      review_process: '🔍',
      finalizing: '⚡',
      completed: '✅',
      failed: '❌'
    };
    return icons[step as keyof typeof icons] || '📝';
  };

  const getStepColor = (step: string) => {
    const colors = {
      initializing: 'text-blue-600',
      analyzing_brief: 'text-purple-600',
      content_generation: 'text-green-600',
      design_creation: 'text-orange-600',
      review_process: 'text-indigo-600',
      finalizing: 'text-yellow-600',
      completed: 'text-green-600',
      failed: 'text-red-600'
    };
    return colors[step as keyof typeof colors] || 'text-gray-600';
  };

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      completed: 'badge-success',
      running: 'badge-warning',
      failed: 'badge-error',
      initialized: 'badge-info'
    };
    
    return `badge ${statusClasses[status as keyof typeof statusClasses] || 'badge-neutral'}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-6xl mx-auto">
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="loading loading-spinner loading-lg text-mm-primary"></div>
              <p className="mt-4 text-[var(--mm-gray-600)]">Loading campaign progress...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !progress) {
    return (
      <div className="min-h-screen bg-[var(--mm-gray-50)] p-6">
        <div className="max-w-6xl mx-auto">
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
      <div className="max-w-6xl mx-auto space-y-6">
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
              <p className="text-[var(--mm-gray-600)]">Real-time campaign generation progress and agent interactions</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="stat">
                <div className="stat-title">Campaign ID</div>
                <div className="stat-value text-lg font-mono">{progress.campaign_id}</div>
              </div>
              <div className="stat">
                <div className="stat-title">Status</div>
                <div className="stat-value">
                  <span className={getStatusBadge(progress.status)}>{progress.status.toUpperCase()}</span>
                </div>
              </div>
              <div className="stat">
                <div className="stat-title">Last Update</div>
                <div className="stat-value text-lg">{new Date(progress.last_update).toLocaleTimeString()}</div>
              </div>
            </div>

            {/* Real-time Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-[var(--mm-gray-700)]">
                  Progress: {progress.progress.completed_steps} / {progress.progress.total_steps} steps
                </span>
                <span className="text-sm text-[var(--mm-gray-600)]">
                  {Math.round((progress.progress.completed_steps / progress.progress.total_steps) * 100)}%
                </span>
              </div>
              <div className="w-full bg-[var(--mm-gray-200)] rounded-full h-3">
                <div 
                  className="bg-mm-primary h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${(progress.progress.completed_steps / progress.progress.total_steps) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Current Step Status */}
        <div className="card-mm">
          <div className="p-6">
            <h3 className="text-xl font-semibold text-[var(--mm-gray-900)] mb-4">Current Step</h3>
            <div className="flex items-center gap-4 p-4 bg-[var(--mm-gray-100)] rounded-lg">
              <div className="text-4xl">{getStepIcon(progress.progress.current_step)}</div>
              <div className="flex-1">
                <h4 className={`text-lg font-semibold ${getStepColor(progress.progress.current_step)}`}>
                  {progress.progress.step_name}
                </h4>
                <p className="text-[var(--mm-gray-600)]">{progress.progress.step_description}</p>
                <p className="text-sm text-[var(--mm-gray-500)] mt-1">
                  Agent: {progress.progress.current_agent || 'System'}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-[var(--mm-gray-500)]">Last Update</div>
                <div className="text-sm font-medium">{new Date(progress.progress.last_update).toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Agent Interactions */}
        <div className="card-mm">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-[var(--mm-gray-900)]">Live Agent Interactions</h3>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-[var(--mm-gray-600)]">Live Updates</span>
              </div>
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {progress.agent_interactions.length === 0 ? (
                <div className="text-center py-8 text-[var(--mm-gray-500)]">
                  <div className="text-4xl mb-2">🤖</div>
                  <p>Waiting for agent interactions...</p>
                </div>
              ) : (
                progress.agent_interactions.map((interaction, index) => (
                  <div 
                    key={index} 
                    className={`p-4 rounded-lg border-l-4 ${
                      interaction.status === 'error' 
                        ? 'border-red-500 bg-red-50' 
                        : interaction.status === 'success'
                        ? 'border-green-500 bg-green-50'
                        : 'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-[var(--mm-gray-900)]">
                            {interaction.agent}
                          </span>
                          <span className={`badge badge-sm ${
                            interaction.status === 'error' ? 'badge-error' :
                            interaction.status === 'success' ? 'badge-success' :
                            'badge-info'
                          }`}>
                            {interaction.action}
                          </span>
                        </div>
                        <p className="text-[var(--mm-gray-700)]">{interaction.message}</p>
                      </div>
                      <div className="text-right text-sm text-[var(--mm-gray-500)]">
                        {new Date(interaction.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Download Section - Only show for completed campaigns */}
        {progress.status === 'completed' && (
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
                    {progress.artifacts_count > 0 ? (
                      <div className="text-center py-4">
                        <div className="text-2xl text-mm-primary mb-2">{progress.artifacts_count}</div>
                        <p className="text-[var(--mm-gray-600)]">Artifacts generated successfully</p>
                      </div>
                    ) : (
                      <div className="text-center py-4 text-[var(--mm-gray-500)]">
                        <p>No artifacts available yet</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Campaign Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="text-3xl text-mm-primary mb-2">{progress.artifacts_count}</div>
              <div className="text-[var(--mm-gray-600)]">Artifacts Generated</div>
            </div>
          </div>
          
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="text-3xl text-mm-secondary mb-2">{progress.revision_count}</div>
              <div className="text-[var(--mm-gray-600)]">Revisions Made</div>
            </div>
          </div>
          
          <div className="card-mm">
            <div className="p-6 text-center">
              <div className="text-3xl text-[var(--mm-gray-700)] mb-2">
                {progress.execution_time > 0 ? `${progress.execution_time.toFixed(1)}s` : '--'}
              </div>
              <div className="text-[var(--mm-gray-600)]">Execution Time</div>
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