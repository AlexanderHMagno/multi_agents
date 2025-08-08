# 🚀 FastAPI Backend for Multi-Agent Campaign Generation

A REST API interface for the Multi-Agent Campaign Generation System, providing endpoints to submit campaign briefs and receive comprehensive marketing campaign outputs.

## 🔐 Authentication

**All campaign-related endpoints require authentication.** The API uses JWT (JSON Web Tokens) for secure authentication.

### Default Users
- **Admin**: `admin` / `admin123` (full access, can manage users)
- **User**: `user1` / `password123` (standard user access)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │    │   FastAPI        │    │   Multi-Agent   │
│   (Frontend)    │◄──►│   Backend        │◄──►│   Workflow      │
│   + Auth        │    │   + JWT Auth     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   File Storage   │
                       │   (outputs/)     │
                       └──────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install API-specific dependencies
pip install -r api/requirements.txt

# Or install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```bash
# Required - OpenRouter API for LLM access
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Optional - OpenAI for DALL-E image generation
OPENAI_API_KEY=sk-xxxxx

# Optional - Model selection
RATIONAL_MODEL=google/gemini-2.5-flash-lite

# Optional - JWT Secret (auto-generated if not provided)
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Start the Server
```bash
# Option 1: Use the startup script (recommended)
python api/start_server.py

# Option 2: Direct start
python api/main.py

# Option 3: Using uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## 🔐 Authentication Endpoints

### Login
```http
POST /api/v1/auth/login
```
Get JWT access token for authentication.

**Request Body:**
```json
{
  "username": "user1",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Register
```http
POST /api/v1/auth/register
```
Register a new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "New User",
  "role": "user"
}
```

### Get Current User
```http
GET /api/v1/auth/me
```
Get current user information (requires authentication).

## 📋 Protected API Endpoints

All campaign endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### 🔍 Health Check
```http
GET /api/v1/health
```
Check API health and configuration status.

### 🚀 Campaign Generation
```http
POST /api/v1/campaigns/generate
```
Submit a campaign brief for generation (requires authentication).

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "product": "AI-Powered Marketing Analytics Platform",
  "client": "DataFlow Analytics",
  "client_website": "https://dataflowanalytics.com",
  "client_logo": "https://placehold.co/200x100?text=DataFlow+Analytics",
  "color_scheme": "blue and white with modern gradients",
  "target_audience": "Marketing professionals and agencies",
  "goals": [
    "Increase platform adoption",
    "Generate qualified leads",
    "Establish thought leadership"
  ],
  "key_features": [
    "Real-time campaign analytics",
    "AI-powered insights",
    "Multi-platform integration"
  ],
  "budget": "$10,000",
  "timeline": "4 months",
  "additional_requirements": "Focus on B2B marketing"
}
```

**Response:**
```json
{
  "campaign_id": "campaign_20241201_143022_12345",
  "status": "started",
  "message": "Campaign generation started successfully. Use the campaign_id to check status and retrieve results.",
  "artifacts": {},
  "created_by": "user1",
  "created_at": "2024-12-01T14:30:22.123456"
}
```

### 📊 Campaign Status
```http
GET /api/v1/campaigns/{campaign_id}/status
```
Get campaign generation status and progress (requires authentication).

### 📋 Campaign Results
```http
GET /api/v1/campaigns/{campaign_id}
```
Get complete campaign results and artifacts (requires authentication).

### 🌐 Download Website
```http
GET /api/v1/campaigns/{campaign_id}/website
```
Download the generated campaign presentation website (requires authentication).

### 📄 Download PDF
```http
GET /api/v1/campaigns/{campaign_id}/pdf
```
Download the generated campaign PDF report (requires authentication).

### 📋 List Campaigns
```http
GET /api/v1/campaigns
```
List all campaigns with their status (requires authentication).

## 👑 Admin Endpoints

Admin users have additional privileges to manage users and access all campaigns.

### List All Users
```http
GET /api/v1/auth/users
```
List all users (admin only).

### Delete User
```http
DELETE /api/v1/auth/users/{username}
```
Delete a user account (admin only).

### Update User Role
```http
PUT /api/v1/auth/users/{username}/role
```
Update user role (admin only).

### Disable User
```http
PUT /api/v1/auth/users/{username}/disable
```
Disable a user account (admin only).

### Enable User
```http
PUT /api/v1/auth/users/{username}/enable
```
Enable a user account (admin only).

## 💻 Client Examples

### Python Client with Authentication
```python
from api.client_example import CampaignAPIClient

# Initialize client
client = CampaignAPIClient("http://localhost:8000")

# Login to get access token
if client.login("user1", "password123"):
    # Submit campaign brief
    campaign_brief = {
        "product": "AI-Powered Marketing Analytics Platform",
        "client": "DataFlow Analytics",
        "target_audience": "Marketing professionals",
        "goals": ["Increase adoption", "Generate leads"],
        "key_features": ["Real-time analytics", "AI insights"]
    }

    response = client.generate_campaign(campaign_brief)
    campaign_id = response["campaign_id"]

    # Wait for completion
    if client.wait_for_completion(campaign_id):
        # Download results
        client.download_website(campaign_id)
        client.download_pdf(campaign_id)
```

### cURL Examples with Authentication
```bash
# 1. Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=password123"

# 2. Use token for campaign generation
TOKEN="your_jwt_token_here"
curl -X POST "http://localhost:8000/api/v1/campaigns/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product": "AI Analytics Platform",
    "client": "DataFlow Analytics",
    "target_audience": "Marketing professionals",
    "goals": ["Increase adoption"],
    "key_features": ["Real-time analytics"]
  }'

# 3. Check status with token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/campaigns/campaign_20241201_143022_12345/status"

# 4. Download website with token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/campaigns/campaign_20241201_143022_12345/website" \
  -o campaign_website.html
```

### JavaScript/Node.js with Authentication
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000'
});

// Login function
async function login(username, password) {
  const response = await client.post('/api/v1/auth/login', 
    `username=${username}&password=${password}`,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }
  );
  return response.data.access_token;
}

// Generate campaign with authentication
async function generateCampaign(token) {
  const response = await client.post('/api/v1/campaigns/generate', {
    product: "AI Analytics Platform",
    client: "DataFlow Analytics",
    target_audience: "Marketing professionals",
    goals: ["Increase adoption"],
    key_features: ["Real-time analytics"]
  }, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.data.campaign_id;
}

// Usage
async function main() {
  const token = await login('user1', 'password123');
  const campaignId = await generateCampaign(token);
  console.log('Campaign ID:', campaignId);
}
```

## 🔧 Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM access |
| `OPENROUTER_BASE_URL` | Yes | OpenRouter API base URL |
| `OPENAI_API_KEY` | No | OpenAI API key for DALL-E image generation |
| `RATIONAL_MODEL` | No | LLM model to use (default: google/gemini-2.5-flash-lite) |
| `JWT_SECRET_KEY` | No | JWT secret key (auto-generated if not provided) |

### Server Configuration
The server runs on:
- **Host**: 0.0.0.0 (accessible from any IP)
- **Port**: 8000
- **Reload**: Enabled for development
- **Log Level**: info
- **Authentication**: JWT-based with 30-minute token expiry

## 🔐 Security Features

### JWT Authentication
- **Token Expiry**: 30 minutes (configurable)
- **Algorithm**: HS256
- **Auto-generated secret**: If not provided in environment
- **Secure password hashing**: bcrypt with salt

### Access Control
- **User isolation**: Users can only access their own campaigns
- **Admin privileges**: Admins can access all campaigns and manage users
- **Role-based access**: User and admin roles
- **Account management**: Enable/disable users, role updates

### Security Headers
- **CORS**: Configured for cross-origin requests
- **WWW-Authenticate**: Proper authentication headers
- **Content-Type**: Strict content type validation

## 📊 Monitoring & Analytics

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-12-01T14:30:22.123456",
  "version": "1.0.0",
  "llm_model": "google/gemini-2.5-flash-lite",
  "openai_available": true,
  "workflow_ready": true,
  "authentication": "enabled"
}
```

### Campaign Status Response
```json
{
  "campaign_id": "campaign_20241201_143022_12345",
  "status": "running",
  "progress": {
    "artifacts_generated": 5,
    "revision_count": 1,
    "execution_time": 45.2
  },
  "estimated_completion": null
}
```

## 🛡️ Error Handling

### Authentication Errors
```json
{
  "detail": "Could not validate credentials"
}
```

```json
{
  "detail": "Incorrect username or password"
}
```

### Authorization Errors
```json
{
  "detail": "Access denied. You can only view your own campaigns."
}
```

```json
{
  "detail": "Not enough permissions"
}
```

### Common Error Responses
```json
{
  "detail": "Campaign not found"
}
```

```json
{
  "detail": "Campaign generation not completed"
}
```

## 🚀 Deployment

### Development
```bash
python api/start_server.py
```

### Production
```bash
# Using gunicorn
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t campaign-api .
docker run -p 8000:8000 campaign-api
```

### Docker Support
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐳 Docker

### Build Image
```bash
# From project root
docker build -t campaign-api .
```

### Run Container
```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/outputs:/app/outputs \
  campaign-api
```

- App: http://localhost:8000
- Docs: http://localhost:8000/docs

### Docker Compose (optional)
Create `docker-compose.yml` in the project root:
```yaml
version: "3.9"
services:
  api:
    build: .
    container_name: campaign-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./outputs:/app/outputs
    restart: unless-stopped
```

Then run:
```bash
docker compose up --build
```

## Development with Docker (Hot Reload)

- Create `.env` in repo root with your API keys and settings.
- Start the API with live-reload and source mounting:

```bash
docker compose up --build
```

Compose mounts the repository into `/app` inside the container and runs:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
```

Any changes you make to the source locally will trigger auto-reload in the container. Generated outputs are stored under `./outputs` on your host (still accessible in the container at `/app/outputs`).

For production, run without `--reload` and avoid mounting the whole repo.

## 🔍 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Check if user exists
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=user1&password=password123"
```

**Token Expired**
```bash
# Re-login to get new token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=user1&password=password123"
```

**Access Denied**
```bash
# Check user role and permissions
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auth/me"
```

**Missing Dependencies**
```bash
pip install -r api/requirements.txt
```

**Environment Variables**
```bash
# Check .env file exists
ls -la .env

# Verify variables are loaded
python -c "import os; print(os.getenv('OPENROUTER_API_KEY'))"
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT Authentication Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [Multi-Agent System Documentation](../README.md)
- [API Interactive Documentation](http://localhost:8000/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

Built with ❤️ using FastAPI, LangChain, and LangGraph 
