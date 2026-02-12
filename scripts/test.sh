#!/bin/bash
set -e

echo "🧪 Running Mission Architecture Simulator Tests..."
echo ""

# Backend tests
echo "📦 Backend Tests (pytest)..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
pytest tests/ -v --cov=app --cov-report=term
cd ..

echo ""

# Frontend tests
echo "🎨 Frontend Tests (jest)..."
cd frontend
if [ -d "node_modules" ]; then
    npm test -- --passWithNoTests
else
    echo "⚠️  Frontend dependencies not installed. Run 'npm install' first."
fi
cd ..

echo ""
echo "✅ All tests complete!"
