# Multi-Agent Campaign Generation System

A comprehensive marketing campaign generation system that uses 17 specialized AI agents to create complete marketing campaigns.

## Project Structure

```
multi_agents/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints and authentication
│   ├── src/                # Core business logic and agents
│   ├── main.py             # Main application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container configuration
├── frontend/               # React frontend
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile          # Production frontend container
│   ├── Dockerfile.dev      # Development frontend container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Production services
├── docker-compose.dev.yml  # Development services
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.8+ (for local backend development)

### Using Docker Compose (Recommended)

1. **Production setup:**
   ```bash
   docker-compose up --build
   ```

2. **Development setup:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## Services

### Backend (Port 8000)
- FastAPI application with JWT authentication
- Multi-agent workflow for campaign generation
- File generation (HTML websites, PDF reports)
- User management and admin functions

### Frontend (Port 3000)
- React application with TypeScript
- User authentication and dashboard
- Campaign creation forms
- Real-time campaign monitoring
- File download functionality

## API Documentation

Comprehensive API documentation is available at:
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- API reference: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Default Users

- **Admin:** `admin` / `admin123`
- **User:** `user1` / `password123`

## Development

### Backend Development
- Located in `backend/` folder
- FastAPI with automatic reload
- Python modules in `src/` folder
- API endpoints in `api/` folder

### Frontend Development
- Located in `frontend/` folder
- React with TypeScript
- Hot reloading in development
- Component-based architecture

### Docker Development
- `docker-compose.dev.yml` for development
- Volume mounts for live code changes
- Hot reloading for both services

## Production Deployment

### Using Production Docker Compose
```bash
docker-compose up --build
```

### Environment Variables
Create a `.env` file in the root directory:
```env
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker Compose
5. Submit a pull request

## License

This project is licensed under the MIT License.