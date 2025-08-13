# Campaign Generator Frontend

A modern React frontend for the Multi-Agent Campaign Generation System, built with Vite and TypeScript.

## Features

- 🚀 **Vite-powered** - Fast development and build times
- ⚛️ **React 18** - Latest React features and hooks
- 🔐 **JWT Authentication** - Secure user authentication
- 📱 **Responsive Design** - Mobile-first approach
- 🎨 **Modern UI** - Clean and intuitive interface
- 📊 **Real-time Updates** - Live campaign monitoring
- 📁 **File Downloads** - Website and PDF downloads

## Tech Stack

- **Frontend Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: CSS3 with custom components
- **Routing**: React Router v6
- **State Management**: React Context + Hooks
- **HTTP Client**: Fetch API with custom wrapper

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Login.tsx       # Authentication login
│   │   ├── Register.tsx    # User registration
│   │   ├── Dashboard.tsx   # Main dashboard
│   │   ├── CampaignGenerator.tsx  # Campaign creation
│   │   ├── CampaignMonitor.tsx    # Campaign monitoring
│   │   └── ProtectedRoute.tsx     # Route protection
│   ├── hooks/              # Custom React hooks
│   │   └── useAuth.tsx     # Authentication hook
│   ├── api/                # API client
│   │   └── client.ts       # HTTP client wrapper
│   ├── types/              # TypeScript definitions
│   │   └── index.ts        # API types and interfaces
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   ├── App.css             # Application styles
│   └── index.css           # Global styles
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── vite.config.ts          # Vite configuration
├── Dockerfile              # Production container
├── Dockerfile.dev          # Development container
└── nginx.conf              # Nginx configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Docker (for containerized development)

### Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Docker Development

1. **Start with Docker Compose:**
   ```bash
   # From project root
   ./start-dev.sh
   ```

2. **Or manually:**
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend integrates with the backend API through the following endpoints:

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Campaigns
- `POST /api/v1/campaigns/generate` - Create new campaign
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `GET /api/v1/campaigns/{id}/status` - Get campaign status
- `GET /api/v1/campaigns/{id}/website` - Download website
- `GET /api/v1/campaigns/{id}/pdf` - Download PDF report

### Utilities
- `GET /api/v1/health` - Health check
- `GET /campaigns/view/{id}` - View campaign website

## Components

### Authentication Components
- **Login**: User authentication form
- **Register**: New user registration
- **ProtectedRoute**: Route protection wrapper

### Campaign Components
- **CampaignGenerator**: Campaign creation form
- **CampaignMonitor**: Campaign status and monitoring
- **Dashboard**: Main application dashboard

### Layout Components
- **App**: Main application wrapper
- **Header**: Application header with navigation

## Styling

The application uses a custom CSS framework with:
- Responsive grid system
- Form styling
- Button components
- Status indicators
- Error and success messages

## Development Features

- **Hot Module Replacement** - Instant updates during development
- **TypeScript** - Type safety and better developer experience
- **ESLint** - Code quality and consistency
- **Source Maps** - Better debugging experience

## Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Preview the build:**
   ```bash
   npm run preview
   ```

3. **Docker production:**
   ```bash
   docker compose up --build
   ```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Campaign Generator
```

## Testing

The application includes:
- TypeScript type checking
- ESLint code quality checks
- Responsive design testing

## Deployment

### Docker Production
```bash
docker compose up --build
```

### Static Hosting
1. Build the application: `npm run build`
2. Deploy the `dist/` folder to your hosting provider

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **API connection**: Verify backend is running on port 8000
3. **Build errors**: Check TypeScript and dependency versions

### Development Tips

- Use the browser's developer tools for debugging
- Check the browser console for API errors
- Verify environment variables are set correctly

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test components in different screen sizes
4. Update documentation for new features

## License

This project is licensed under the MIT License. 