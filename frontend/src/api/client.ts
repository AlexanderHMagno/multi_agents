import { 
  Token, 
  User, 
  UserCreate, 
  CampaignBrief, 
  CampaignResponse, 
  CampaignStatus, 
  CampaignListResponse,
  HealthCheckResponse,
  ApiError 
} from '../types';

class ApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>).Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = 'API request failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If error response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      
      const error: ApiError = {
        detail: errorMessage,
        status: response.status
      };
      throw error;
    }

    return response.json();
  }

  // Authentication methods
  async login(username: string, password: string): Promise<Token> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = 'Login failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      
      const error: ApiError = {
        detail: errorMessage,
        status: response.status
      };
      throw error;
    }

    const token = await response.json();
    this.setToken(token.access_token);
    return token;
  }

  async register(userData: UserCreate): Promise<User> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Campaign methods
  async generateCampaign(brief: CampaignBrief): Promise<CampaignResponse> {
    return this.request<CampaignResponse>('/api/v1/campaigns/generate', {
      method: 'POST',
      body: JSON.stringify(brief),
    });
  }

  async getCampaign(campaignId: string): Promise<CampaignResponse> {
    return this.request<CampaignResponse>(`/api/v1/campaigns/${campaignId}`);
  }

  async getCampaignStatus(campaignId: string): Promise<CampaignStatus> {
    return this.request<CampaignStatus>(`/api/v1/campaigns/${campaignId}/status`);
  }

  async listCampaigns(): Promise<CampaignListResponse> {
    return this.request<CampaignListResponse>('/api/v1/campaigns');
  }

  async downloadWebsite(campaignId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/campaigns/${campaignId}/website`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to download website');
    }

    return response.blob();
  }

  async downloadPDF(campaignId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/campaigns/${campaignId}/pdf`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to download PDF');
    }

    return response.blob();
  }

  // Utility methods
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/api/v1/health');
  }

  // View campaign website (public)
  async viewCampaignWebsite(campaignId: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/campaigns/view/${campaignId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch campaign website');
    }

    return response.text();
  }
}

export const apiClient = new ApiClient(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'); 