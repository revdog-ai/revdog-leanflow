#!/bin/bash
# Run all tests

set -e

echo "🧪 Running all tests..."

# Backend tests
echo ""
echo "📦 Backend tests (Python)..."
cd backend && pytest -v --cov=. --cov-report=term-missing

# Frontend tests
echo ""
echo "🎨 Frontend tests (TypeScript)..."
cd ../frontend && npm test

echo ""
echo "✅ All tests passed!"

