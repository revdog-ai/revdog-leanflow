#!/bin/bash
# Build production images

set -e

echo "🏗️  Building production images..."

# Build backend
echo "Building backend..."
docker build -t revdog-leanflow-backend:latest ./backend

# Build frontend
echo "Building frontend..."
docker build -t revdog-leanflow-frontend:latest ./frontend

echo "✅ Production images built successfully!"
echo ""
echo "To run in production:"
echo "  docker-compose -f docker-compose.prod.yml up -d"

