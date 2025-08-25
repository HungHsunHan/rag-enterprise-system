# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Primary Commands (from root directory)
- `npm run dev` - Start both frontend (port 3000) and backend (port 8001) with hot reload
- `npm run dev:frontend` - Start only React frontend on port 3000
- `npm run dev:backend` - Start only FastAPI backend on port 8001
- `npm run build` - Build frontend for production
- `npm run test` - Run all tests (frontend + backend)
- `npm run lint` - Lint all code using ESLint + Ruff
- `npm run format` - Format all code using Prettier + Black

### Backend Commands (from apps/backend/)
- `python -m alembic upgrade head` - Apply database migrations
- `python -m alembic revision --autogenerate -m "description"` - Create new migration
- `python -m pytest` - Run backend tests
- `python -m pytest --cov=app tests/` - Run tests with coverage
- `black .` - Format Python code
- `ruff check .` - Lint Python code
- `ruff check . --fix` - Fix Python linting issues
- `mypy .` - Type checking

### Database Commands
- `docker-compose up -d postgres redis` - Start database services
- `docker-compose exec postgres psql -U postgres -d hr_chatbot` - Access database
- `docker-compose exec -T postgres psql -U postgres -d hr_chatbot < create-dev-data.sql` - Load dev data

## Architecture Overview

This is a **multi-tenant enterprise RAG system** with complete data isolation between companies.

### Tech Stack
- **Frontend**: React 18 + TypeScript + Vite + Material-UI + Zustand
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + PGVector + Alembic
- **AI/ML**: OpenRouter API + Sentence Transformers + Vector search
- **Infrastructure**: Docker Compose + Redis caching

### Project Structure
```
apps/
├── frontend/           # React app (port 3000 dev, 4000 prod)
│   ├── src/api/       # Backend API clients
│   ├── src/components/ # Reusable UI components
│   ├── src/pages/     # Page components (admin/ subfolder)
│   ├── src/store/     # Zustand state management
│   └── src/styles/    # Material-UI theme
└── backend/           # FastAPI app (port 8001 dev, 9000 prod)
    ├── app/api/       # Route handlers (admin.py, auth.py, chat.py)
    ├── app/core/      # Config, deps, security
    ├── app/db/        # SQLAlchemy models and database
    ├── app/schemas/   # Pydantic validation models
    ├── app/services/  # Business logic layer
    ├── alembic/       # Database migrations
    └── tests/         # 46+ unit tests with >90% coverage
```

### Key Architecture Concepts

#### Multi-Tenant Data Isolation
- **Company-scoped access**: All queries automatically filter by `company_id`
- **Shared documents**: Documents marked as shared (共同) accessible across companies
- **Role-based access**: Admins have global access, employees only see their company data
- **Database isolation**: Every query includes company context to prevent data leakage

#### RAG System Design
- **Document processing**: Two-phase workflow (upload → configure chunking → process)
- **Vector search**: PGVector extension with 384-dimensional embeddings
- **Context building**: Smart assembly from company-relevant + shared documents only
- **Model management**: Dynamic LLM model configuration via admin dashboard

#### Authentication Flow
- **Admin**: Email/password → JWT with admin role
- **Employee**: Employee ID only → JWT with company context
- **JWT tokens**: Include `user_id`, `company_id`, `role` for authorization

## Database Schema

Core tables with multi-tenant design:
- `companies` - Tenant organizations
- `admins` - System administrators (global access)
- `users` - Company employees with names and employee IDs
- `knowledge_documents` - Uploaded files (company-scoped or shared)
- `document_chunks` - Text segments with vector embeddings (company-scoped)
- `llm_models` - Dynamic model configuration
- `feedback_logs` - User interaction tracking

**Critical**: All data access queries MUST include company filtering except for admin operations.

## Development Environment Setup

### Prerequisites
- Node.js >= 20.0.0, npm >= 10.0.0
- Python 3.9+ (conda environment recommended)
- Docker & Docker Compose

### Quick Setup
```bash
# Setup environment
cp .env.example .env
# Edit .env with OpenRouter API key

# Start database services
docker-compose up -d postgres redis

# Backend setup
cd apps/backend
conda create -n rag-system python=3.11
conda activate rag-system
pip install -r requirements.txt
python -m alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Load dev data and start
cd ../..
docker-compose exec -T postgres psql -U postgres -d hr_chatbot < create-dev-data.sql
npm run dev
```

## Testing Strategy

- **46+ comprehensive tests** covering multi-tenant isolation, RAG scoping, auth flows
- **Frontend**: Vitest for unit tests
- **Backend**: Pytest with async support, coverage reporting
- **Test pattern**: Business logic in services, API routes are thin controllers

## Key Files to Understand

### Backend Core
- `apps/backend/app/main.py` - FastAPI application entry point
- `apps/backend/app/core/config.py` - Environment configuration
- `apps/backend/app/db/models.py` - SQLAlchemy database models
- `apps/backend/app/services/rag_service.py` - RAG query processing logic
- `apps/backend/app/services/document_processor.py` - Document chunking and embedding

### Frontend Core  
- `apps/frontend/src/main.tsx` - React application entry
- `apps/frontend/src/store/authStore.ts` - Authentication state management
- `apps/frontend/src/pages/ChatPage.tsx` - Employee chat interface
- `apps/frontend/src/pages/AdminDashboard.tsx` - Admin overview
- `apps/frontend/src/api/client.ts` - API client configuration

## Environment Variables

Required for development (see .env.example):
```bash
# Required: Get free key from openrouter.ai
OPENROUTER_API_KEY=your-openrouter-key

# Database (defaults work for docker-compose)
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_chatbot

# Security (change in production)
SECRET_KEY=your-jwt-secret-key
```

## Production Deployment

Uses `docker-compose.production.yml` with:
- Frontend: Nginx-served React build (port 4000)
- Backend: Uvicorn FastAPI server (port 9000) 
- Database: PostgreSQL with PGVector (port 5433)
- Cache: Redis (port 6380)

## Code Conventions

- **Python**: Black formatting, Ruff linting, type hints with mypy
- **TypeScript**: ESLint + Prettier, strict TypeScript configuration
- **API**: RESTful design with Pydantic validation
- **Database**: Alembic migrations, no raw SQL in business logic
- **Testing**: One test file per service/component, descriptive test names

## Multi-Tenant Development Guidelines

**Always consider company context when:**
- Writing database queries (include `company_id` filters)
- Implementing new features (respect data isolation)
- Adding API endpoints (validate user's company access)
- Testing (verify cross-company data leakage prevention)

**Shared document pattern:**
- Documents with `company_id = NULL` are shared across all companies
- Use joins to include both company-specific AND shared documents
- UI shows shared documents with special indicators (共同)