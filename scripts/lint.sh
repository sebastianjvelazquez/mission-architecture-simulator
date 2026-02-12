#!/bin/bash
set -e

echo "🔍 Running Code Quality Checks..."
echo ""

# Backend linting
echo "📦 Backend Linting (flake8, black, isort)..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "  - Running flake8..."
flake8 app --max-line-length=100 --count

echo "  - Checking black formatting..."
black --check app

echo "  - Checking import sorting..."
isort --check-only app

cd ..

echo ""

# Frontend linting
echo "🎨 Frontend Linting (eslint)..."
cd frontend
if [ -d "node_modules" ]; then
    npm run lint
else
    echo "⚠️  Frontend dependencies not installed. Run 'npm install' first."
fi
cd ..

echo ""
echo "✅ All linting checks passed!"
