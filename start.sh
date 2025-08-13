#!/bin/bash

echo "🚀 Starting Multi-Agent Campaign Generation System..."

echo "📦 Building and starting services..."
docker compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Services are starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Check service status:"
echo "   docker compose ps"
echo ""
echo "📋 View logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker compose down" 