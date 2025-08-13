# Multi-Agent Campaign Generation API Documentation

## Overview

The Multi-Agent Campaign Generation API is a FastAPI-based REST API that uses 17 specialized AI agents to create comprehensive marketing campaigns. This API provides authentication, campaign generation, and result retrieval endpoints.

**Base URL:** `http://localhost:8000` (development)  
**API Version:** `v1`  
**Authentication:** JWT Bearer Token

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [React Integration Examples](#react-integration-examples)
- [Testing](#testing)

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require a valid JWT token in the Authorization header.

### Authentication Flow

1. **Register** a new user account
2. **Login** to receive a JWT token
3. **Include** the token in subsequent requests as `Authorization: Bearer <token>`

### Default Users (for testing)

- **Admin:** `admin` / `admin123`
- **User:** `user1` / `password123`

## Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string (optional)",
  "role": "user (default)"
}
```

**Response:**
```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "disabled": false,
  "role": "string"
}
```

#### POST `/api/v1/auth/login`

Login to receive a JWT access token.

**Request Body (form-data):**
```
username: string
password: string
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

#### GET `/api/v1/auth/me`

Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "disabled": false,
  "role": "string"
}
```

### Campaign Endpoints

#### POST `/api/v1/campaigns/generate`

Generate a new marketing campaign (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "product": "string (required)",
  "client": "string (required)",
  "client_website": "string (optional)",
  "client_logo": "string (optional)",
  "color_scheme": "string (optional, default: 'professional')",
  "target_audience": "string (required)",
  "goals": ["string"] (required),
  "key_features": ["string"] (required),
  "budget": "string (optional, default: '$5,000')",
  "timeline": "string (optional, default: '3 months')",
  "additional_requirements": "string (optional)"
}
```

**Response:**
```json
{
  "campaign_id": "string",
  "status": "started",
  "message": "Campaign generation started successfully. Use the campaign_id to check status and retrieve results.",
  "artifacts": {},
  "website_url": "string",
  "pdf_url": "string",
  "execution_time": null,
  "quality_score": null,
  "revision_count": null,
  "created_at": "string (ISO timestamp)",
  "created_by": "string"
}
```

#### GET `/api/v1/campaigns/{campaign_id}`

Get campaign results and status (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "campaign_id": "string",
  "status": "string (initialized|running|completed|failed)",
  "message": "string",
  "artifacts": {},
  "website_url": "string",
  "pdf_url": "string",
  "execution_time": "number",
  "quality_score": "number",
  "revision_count": "number",
  "created_at": "string",
  "created_by": "string"
}
```

#### GET `/api/v1/campaigns/{campaign_id}/status`

Get campaign status and progress (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "campaign_id": "string",
  "status": "string",
  "progress": {
    "artifacts_generated": "number",
    "revision_count": "number",
    "execution_time": "number"
  },
  "estimated_completion": "string"
}
```

#### GET `/api/v1/campaigns/{campaign_id}/website`

Download the generated campaign website (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** HTML file download

#### GET `/api/v1/campaigns/{campaign_id}/pdf`

Download the generated campaign PDF report (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** PDF file download

#### GET `/api/v1/campaigns`

List all campaigns with their status (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": "string",
      "status": "string",
      "created_at": "string",
      "completed_at": "string",
      "execution_time": "number",
      "artifacts_count": "number",
      "created_by": "string"
    }
  ],
  "total": "number",
  "completed": "number",
  "running": "number",
  "failed": "number"
}
```

### Utility Endpoints

#### GET `/api/v1/health`

Check API health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "string",
  "version": "1.0.0",
  "llm_model": "string",
  "openai_available": "boolean",
  "workflow_ready": "boolean",
  "authentication": "enabled"
}
```

#### GET `/campaigns/view/{campaign_id}`

View the generated campaign website in the browser (public access).

**Response:** HTML content

## Data Models

### CampaignBrief

```typescript
interface CampaignBrief {
  product: string;                    // Product or service name
  client: string;                     // Client company name
  client_website?: string;            // Client website URL
  client_logo?: string;               // Client logo URL
  color_scheme?: string;              // Preferred color scheme (default: "professional")
  target_audience: string;            // Target audience description
  goals: string[];                    // Campaign goals
  key_features: string[];             // Key product features
  budget?: string;                    // Campaign budget (default: "$5,000")
  timeline?: string;                  // Campaign timeline (default: "3 months")
  additional_requirements?: string;    // Additional requirements or notes
}
```

### CampaignResponse

```typescript
interface CampaignResponse {
  campaign_id: string;                // Unique campaign identifier
  status: string;                     // Generation status
  message: string;                    // Status message
  artifacts: Record<string, any>;     // Generated campaign artifacts
  website_url?: string;               // Generated website URL
  pdf_url?: string;                   // Generated PDF URL
  execution_time?: number;            // Execution time in seconds
  quality_score?: number;             // Campaign quality score
  revision_count?: number;            // Number of revisions performed
  created_at: string;                 // Creation timestamp
  created_by: string;                 // Username who created the campaign
}
```

### User

```typescript
interface User {
  username: string;                   // Unique username
  email: string;                      // User email address
  full_name?: string;                 // User's full name
  disabled: boolean;                  // Account disabled status
  role: string;                       // User role
}
```

### Token

```typescript
interface Token {
  access_token: string;               // JWT access token
  token_type: string;                 // Token type (always "bearer")
}
```

## Error Handling

The API returns standard HTTP status codes and error messages:

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

## React Integration Examples

### Setting up API Client

```typescript
// api/client.ts
class ApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor(baseUrl: string) {
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
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
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
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const token = await response.json();
    this.setToken(token.access_token);
    return token;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }): Promise<User> {
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

  async listCampaigns(): Promise<{
    campaigns: any[];
    total: number;
    completed: number;
    running: number;
    failed: number;
  }> {
    return this.request('/api/v1/campaigns');
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
}

export const apiClient = new ApiClient('http://localhost:8000');
```

### Authentication Hook

```typescript
// hooks/useAuth.ts
import { useState, useEffect, createContext, useContext } from 'react';
import { apiClient } from '../api/client';
import { User, Token } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        apiClient.clearToken();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const token = await apiClient.login(username, password);
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      await apiClient.register(userData);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    apiClient.clearToken();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

### Campaign Generation Component

```typescript
// components/CampaignGenerator.tsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { CampaignBrief } from '../types';

export const CampaignGenerator: React.FC = () => {
  const [brief, setBrief] = useState<CampaignBrief>({
    product: '',
    client: '',
    target_audience: '',
    goals: [''],
    key_features: [''],
  });
  const [loading, setLoading] = useState(false);
  const [campaignId, setCampaignId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await apiClient.generateCampaign(brief);
      setCampaignId(response.campaign_id);
      alert('Campaign generation started! Check the status to monitor progress.');
    } catch (error) {
      console.error('Failed to generate campaign:', error);
      alert('Failed to generate campaign. Please try again.');
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

  return (
    <div className="campaign-generator">
      <h2>Generate New Campaign</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Product/Service:</label>
          <input
            type="text"
            value={brief.product}
            onChange={(e) => setBrief(prev => ({ ...prev, product: e.target.value }))}
            required
          />
        </div>

        <div className="form-group">
          <label>Client Company:</label>
          <input
            type="text"
            value={brief.client}
            onChange={(e) => setBrief(prev => ({ ...prev, client: e.target.value }))}
            required
          />
        </div>

        <div className="form-group">
          <label>Target Audience:</label>
          <textarea
            value={brief.target_audience}
            onChange={(e) => setBrief(prev => ({ ...prev, target_audience: e.target.value }))}
            required
          />
        </div>

        <div className="form-group">
          <label>Campaign Goals:</label>
          {brief.goals.map((goal, index) => (
            <input
              key={index}
              type="text"
              value={goal}
              onChange={(e) => updateGoal(index, e.target.value)}
              placeholder="Enter campaign goal"
              required
            />
          ))}
          <button type="button" onClick={addGoal}>Add Goal</button>
        </div>

        <div className="form-group">
          <label>Key Features:</label>
          {brief.key_features.map((feature, index) => (
            <input
              key={index}
              type="text"
              value={feature}
              onChange={(e) => updateFeature(index, e.target.value)}
              placeholder="Enter key feature"
              required
            />
          ))}
          <button type="button" onClick={addFeature}>Add Feature</button>
        </div>

        <div className="form-group">
          <label>Color Scheme:</label>
          <select
            value={brief.color_scheme}
            onChange={(e) => setBrief(prev => ({ ...prev, color_scheme: e.target.value }))}
          >
            <option value="professional">Professional</option>
            <option value="creative">Creative</option>
            <option value="modern">Modern</option>
            <option value="vintage">Vintage</option>
          </select>
        </div>

        <div className="form-group">
          <label>Budget:</label>
          <input
            type="text"
            value={brief.budget}
            onChange={(e) => setBrief(prev => ({ ...prev, budget: e.target.value }))}
            placeholder="$5,000"
          />
        </div>

        <div className="form-group">
          <label>Timeline:</label>
          <input
            type="text"
            value={brief.timeline}
            onChange={(e) => setBrief(prev => ({ ...prev, timeline: e.target.value }))}
            placeholder="3 months"
          />
        </div>

        <div className="form-group">
          <label>Additional Requirements:</label>
          <textarea
            value={brief.additional_requirements || ''}
            onChange={(e) => setBrief(prev => ({ ...prev, additional_requirements: e.target.value }))}
            placeholder="Any additional requirements or notes..."
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Campaign'}
        </button>
      </form>

      {campaignId && (
        <div className="success-message">
          <h3>Campaign Started!</h3>
          <p>Campaign ID: {campaignId}</p>
          <p>Check the campaign status to monitor progress and download results.</p>
        </div>
      )}
    </div>
  );
};
```

### Campaign Status Monitor

```typescript
// components/CampaignMonitor.tsx
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { CampaignResponse, CampaignStatus } from '../types';

interface CampaignMonitorProps {
  campaignId: string;
}

export const CampaignMonitor: React.FC<CampaignMonitorProps> = ({ campaignId }) => {
  const [campaign, setCampaign] = useState<CampaignResponse | null>(null);
  const [status, setStatus] = useState<CampaignStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        const [campaignData, statusData] = await Promise.all([
          apiClient.getCampaign(campaignId),
          apiClient.getCampaignStatus(campaignId)
        ]);
        setCampaign(campaignData);
        setStatus(statusData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch campaign');
      } finally {
        setLoading(false);
      }
    };

    fetchCampaign();
    
    // Poll for status updates every 5 seconds if campaign is running
    const interval = setInterval(() => {
      if (status?.status === 'running') {
        fetchCampaign();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [campaignId, status?.status]);

  const downloadWebsite = async () => {
    try {
      const blob = await apiClient.downloadWebsite(campaignId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${campaignId}_website.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download website');
    }
  };

  const downloadPDF = async () => {
    try {
      const blob = await apiClient.downloadPDF(campaignId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${campaignId}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download PDF');
    }
  };

  if (loading) {
    return <div>Loading campaign...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!campaign) {
    return <div>Campaign not found</div>;
  }

  return (
    <div className="campaign-monitor">
      <h2>Campaign Status: {campaign.status}</h2>
      
      <div className="campaign-info">
        <p><strong>Campaign ID:</strong> {campaign.campaign_id}</p>
        <p><strong>Created:</strong> {new Date(campaign.created_at).toLocaleString()}</p>
        <p><strong>Created By:</strong> {campaign.created_by}</p>
        {campaign.execution_time && (
          <p><strong>Execution Time:</strong> {campaign.execution_time.toFixed(2)} seconds</p>
        )}
        {campaign.quality_score && (
          <p><strong>Quality Score:</strong> {campaign.quality_score}</p>
        )}
        {campaign.revision_count && (
          <p><strong>Revisions:</strong> {campaign.revision_count}</p>
        )}
      </div>

      {status?.progress && (
        <div className="progress-info">
          <h3>Progress</h3>
          <p>Artifacts Generated: {status.progress.artifacts_generated}</p>
          <p>Revision Count: {status.progress.revision_count}</p>
          <p>Execution Time: {status.progress.execution_time?.toFixed(2)} seconds</p>
        </div>
      )}

      {campaign.status === 'completed' && (
        <div className="download-section">
          <h3>Download Results</h3>
          <button onClick={downloadWebsite}>Download Website</button>
          <button onClick={downloadPDF}>Download PDF Report</button>
          
          <div className="artifacts">
            <h4>Generated Artifacts:</h4>
            <pre>{JSON.stringify(campaign.artifacts, null, 2)}</pre>
          </div>
        </div>
      )}

      {campaign.status === 'failed' && (
        <div className="error-section">
          <h3>Campaign Generation Failed</h3>
          <p>{campaign.message}</p>
        </div>
      )}
    </div>
  );
};
```

## Testing

### Using the Default Users

1. **Login as Admin:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

2. **Login as User:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user1&password=password123"
   ```

### Testing Campaign Generation

```bash
# Generate a campaign (replace TOKEN with actual JWT token)
curl -X POST "http://localhost:8000/api/v1/campaigns/generate" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Eco-Friendly Water Bottle",
    "client": "GreenLife Inc",
    "target_audience": "Environmentally conscious consumers aged 25-45",
    "goals": ["Increase brand awareness", "Drive online sales"],
    "key_features": ["BPA-free", "Reusable", "Sustainable materials"]
  }'
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/health"
```

## Development Setup

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Required Python packages (see `api/requirements.txt`)

### Running the API

1. **Install dependencies:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Environment Variables

Create a `.env` file in the `api` directory:

```env
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

## Notes

- The API currently uses in-memory storage for campaigns and users. In production, implement a proper database.
- Campaign generation is asynchronous and may take several minutes to complete.
- The API includes CORS middleware configured for development. Configure appropriately for production.
- JWT tokens expire after 120 minutes by default.
- Admin users have access to all campaigns and user management features.

## Support

For API-related issues or questions, refer to:
- Interactive API documentation at `/docs`
- Alternative documentation at `/redoc`
- Health check endpoint at `/api/v1/health` 