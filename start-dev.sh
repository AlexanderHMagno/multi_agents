#!/bin/bash

echo "🚀 Starting Multi-Agent Campaign Generation System (Development Mode)..."

echo "📦 Building and starting development services..."
docker compose -f docker-compose.dev.yml up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 15

echo "✅ Development services are starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000 (with hot-reload)"
echo "🔧 Backend API: http://localhost:8000 (with auto-reload)"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔄 Development features:"
echo "   - Frontend hot-reloading enabled"
echo "   - Backend auto-reload enabled"
echo "   - Volume mounts for live code changes"
echo ""
echo "🔍 Check service status:"
echo "   docker compose -f docker-compose.dev.yml ps"
echo ""
echo "📋 View logs:"
echo "   docker compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker compose -f docker-compose.dev.yml down" 