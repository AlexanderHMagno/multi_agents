import React from 'react';

// API Response Types
export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  username: string;
  email: string;
  full_name?: string;
  disabled: boolean;
  role: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role: string;
}

export interface CampaignBrief {
  campaign_name: string;
  target_audience: string;
  industry: string;
  campaign_goals: string;
  key_features: string[];
  tone: string;
  budget_range: string;
  timeline: string;
}

export interface CampaignResponse {
  campaign_id: string;
  status: string;
  message: string;
  artifacts: Record<string, any>;
  website_url?: string;
  pdf_url?: string;
  execution_time?: number;
  quality_score?: number;
  revision_count?: number;
  created_at: string;
  created_by: string;
}

export interface CampaignStatus {
  campaign_id: string;
  status: string;
  progress?: {
    artifacts_generated: number;
    revision_count: number;
    execution_time: number;
  };
  estimated_completion?: string;
}

export interface CampaignListResponse {
  campaigns: Array<{
    campaign_id: string;
    status: string;
    created_at: string;
    completed_at?: string;
    execution_time?: number;
    artifacts_count: number;
    created_by: string;
  }>;
  total: number;
  completed: number;
  running: number;
  failed: number;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
  llm_model: string;
  openai_available: boolean;
  workflow_ready: boolean;
  authentication: string;
}

// Component Props Types
export interface ProtectedRouteProps {
  children: React.ReactNode;
}

export interface CampaignMonitorProps {
  campaignId: string;
}

// Form Types
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role: string;
}

// Error Types
export interface ApiError {
  detail: string;
  status?: number;
} 