#!/bin/bash

# HR Chatbot Development Setup Script

echo "🚀 Setting up HR Chatbot development environment..."

# Define conda Python path
CONDA_PYTHON="/usr/local/Caskroom/miniforge/base/envs/llm/bin/python"
CONDA_PIP="/usr/local/Caskroom/miniforge/base/envs/llm/bin/pip"

# Check if conda environment exists
if [ ! -f "$CONDA_PYTHON" ]; then
    echo "❌ Conda environment not found at $CONDA_PYTHON"
    echo "Please make sure the 'llm' conda environment is created and available."
    exit 1
fi

echo "✅ Using conda environment: $CONDA_PYTHON"

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

# Wait for PostgreSQL to be ready (with timeout)
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout=60
count=0
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    if [ $count -ge $timeout ]; then
        echo "❌ PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    count=$((count + 1))
done

echo "✅ PostgreSQL is ready!"

# Initialize database with development data
echo "📦 Initializing database with development data..."
if [ -f "create-dev-data.sql" ]; then
    docker-compose exec -T postgres psql -U postgres -d hr_chatbot < create-dev-data.sql > /dev/null 2>&1
    echo "✅ Database initialized with development data"
else
    echo "⚠️ create-dev-data.sql not found, skipping database initialization"
fi

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd apps/frontend
npm install
cd ../..

# Install backend dependencies using conda environment
echo "📦 Installing backend dependencies using conda environment..."
cd apps/backend

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing from requirements.txt..."
    $CONDA_PIP install -r requirements.txt
else
    echo "📦 Installing basic dependencies..."
    $CONDA_PIP install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-multipart passlib bcrypt python-jose sentence-transformers redis httpx pydantic-settings python-dotenv
fi

# Install additional dependencies for vector database
echo "📦 Installing pgvector support..."
$CONDA_PIP install pgvector

cd ../..

echo "🎉 Development environment setup complete!"
echo ""
echo "Environment details:"
echo "  Python: $CONDA_PYTHON"
echo "  Conda env: llm"
echo "  Database: PostgreSQL (localhost:5432)"
echo "  Redis: localhost:6379"
echo ""
echo "Development accounts created:"
echo "  Admin: admin@dev.com / admin123"
echo "  Employees: EMP001, EMP002, DEV001, TEST001"
echo ""
echo "To start the development servers:"
echo "  npm run dev           # Start both frontend and backend"
echo "  npm run dev:frontend  # Start only frontend"
echo "  npm run dev:backend   # Start only backend"
echo ""
echo "To run the database migrations:"
echo "  cd apps/backend && $CONDA_PYTHON -m alembic upgrade head"