#!/bin/bash

# HR Chatbot Development Setup Script

echo "🚀 Setting up HR Chatbot development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start database services
echo "📦 Starting database services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done

echo "✅ PostgreSQL is ready!"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd apps/frontend
npm install
cd ../..

# Install backend dependencies (if using pip)
echo "📦 Installing backend dependencies..."
cd apps/backend

# Check if we're in a virtual environment, if not create one
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
    source venv/bin/activate
fi

# Install dependencies using pip (fallback if poetry not available)
if command -v poetry &> /dev/null; then
    echo "📦 Installing with Poetry..."
    poetry install
else
    echo "📦 Installing with pip..."
    pip install -r requirements.txt 2>/dev/null || echo "⚠️ requirements.txt not found, using pyproject.toml"
fi

cd ../..

echo "🎉 Development environment setup complete!"
echo ""
echo "To start the development servers:"
echo "  npm run dev           # Start both frontend and backend"
echo "  npm run dev:frontend  # Start only frontend"
echo "  npm run dev:backend   # Start only backend"
echo ""
echo "To run the database migrations:"
echo "  cd apps/backend && alembic upgrade head"