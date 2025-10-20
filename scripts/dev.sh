#!/bin/bash
# Development environment startup script

set -e

echo "🚀 Starting RevDog LeanFlow development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from env.example..."
    cp env.example .env
    echo "✅ Created .env file. Please update with your Zerodha API credentials."
fi

# Start all services with docker-compose
echo "📦 Starting services with Docker Compose..."
docker-compose up --build

echo "✅ Development environment is running!"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

