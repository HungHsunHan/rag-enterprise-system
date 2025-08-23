# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Initial setup - runs database and installs dependencies
./scripts/dev-setup.sh

# Start development servers
npm run dev                 # Both frontend and backend
npm run dev:frontend        # Frontend only (port 3000)
npm run dev:backend         # Backend only (port 8000)
```

### Backend Development
```bash
cd apps/backend


# Testing
python -m pytest           # Run all tests
python -m pytest tests/test_specific.py  # Run specific test

# Code quality
black .                     # Format code
ruff check .               # Lint code
ruff check . --fix         # Fix linting issues
mypy .                     # Type checking
```

### Frontend Development
```bash
cd apps/frontend

# Development
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build

# Code quality
npm run lint               # Lint code
npm run format             # Format code with Prettier
npm run test               # Run tests
```

### Database Management
```bash
# Start database services
docker-compose up -d postgres redis

# Access PostgreSQL directly
docker-compose exec postgres psql -U postgres -d hr_chatbot
```

## Architecture Overview

This is a **monolithic application** in a **monorepo** structure implementing an **HR internal Q&A system** with RAG (Retrieval-Augmented Generation) capabilities.

### Core Architecture Principles

1. **Multi-tenant Data Isolation**: CRITICAL SECURITY REQUIREMENT
   - ALL database queries MUST include `WHERE company_id = :company_id` filtering
   - No exceptions - this prevents cross-tenant data leakage

2. **Repository Pattern**: All database access goes through repository classes in `app/db/`
   - Never use SQLAlchemy session directly in API routes or services
   - Use dependency injection for database access

3. **Configuration Management**: All settings accessed through `app/core/config.py`
   - Never use `os.environ.get()` directly in code
   - All environment variables defined in Settings class

### Key Components

#### Backend (`apps/backend/`)
- **FastAPI** application with automatic OpenAPI documentation
- **SQLAlchemy** ORM with **PostgreSQL + PGVector** for vector storage
- **JWT authentication** for both admins and employees
- **RAG pipeline** using sentence-transformers and LLM APIs
- **Multi-format document processing** (.pdf, .docx, .txt)

#### Frontend (`apps/frontend/`)
- **React + TypeScript** with **Vite** build system
- **MUI (Material-UI)** component library for UI
- **Zustand** for state management
- **React Router** for navigation

#### Database Schema
- `companies` - Multi-tenant organizations
- `admins` - System administrators (global access)
- `users` - Employees (company-scoped access)
- `knowledge_documents` - Uploaded files
- `document_chunks` - Text segments with vector embeddings
- `feedback_logs` - User feedback on Q&A pairs

## Environment Configuration

### Required Environment Variables

```bash
# LLM API Configuration (OpenRouter)
OPENROUTER_API_KEY=your-openrouter-api-key-here
LLM_MODEL=microsoft/phi-3-mini-128k-instruct:free

# Embedding Configuration (Free Models)
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
EMBEDDING_DIMENSION=384

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_chatbot

# Security
SECRET_KEY=your-secret-key-change-this-in-production
```

### Alternative Free LLM Models (via OpenRouter)
- `microsoft/phi-3-mini-128k-instruct:free` (default)
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

### Alternative Free Embedding Models
- `sentence-transformers/paraphrase-MiniLM-L3-v2` (default, 384 dimensions)
- `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- `sentence-transformers/all-MiniLM-L12-v2` (384 dimensions, more accurate but slower)

## Critical Security Rules

These rules MUST be followed without exception:

1. **Multi-tenant Filtering**: Every company-related query MUST filter by `company_id`
2. **No Direct Environment Access**: Use `settings` object from `app/core/config.py`
3. **Repository Pattern**: All DB access through repository classes
4. **Structured Error Handling**: Use custom exceptions, handled by global middleware
5. **No Sensitive Logging**: Never log passwords, API keys, or tokens

## Development Workflow

### Adding New Features
1. Update database models in `app/db/models.py` if needed
2. Create/update Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add API endpoints in `app/api/`
5. Update frontend components and pages
6. Write tests for all layers
7. Update API documentation

### Testing Strategy
- **Unit tests**: >80% coverage for backend business logic
- **Integration tests**: API endpoints with real database
- **E2E tests**: Critical user flows with Playwright
- **Database tests**: Use **Testcontainers** for PostgreSQL+PGVector

### Code Quality Standards
- **Backend**: Black formatting, Ruff linting, MyPy type checking
- **Frontend**: Prettier formatting, ESLint linting
- **Pre-commit hooks**: All quality checks must pass before commit

## Technology Stack Details

### AI/ML Components
- **Embedding Model**: `sentence-transformers/paraphrase-MiniLM-L3-v2` (384 dimensions, free model)
- **Vector Database**: PostgreSQL with PGVector extension
- **LLM Integration**: OpenRouter API with `microsoft/phi-3-mini-128k-instruct:free` (free model)
  - OpenRouter provides access to multiple LLM providers through a unified API
  - No OpenAI dependency required - uses standard HTTP requests via httpx
  - Configurable model selection through environment variables
- **Document Processing**: PyPDF, python-docx for text extraction
- **Text Chunking**: Configurable chunk size (default 1000 chars, 200 overlap)

### Infrastructure
- **Development**: Docker Compose with PostgreSQL and Redis
- **Deployment**: TBD (cloud deployment deferred for MVP)
- **Monitoring**: Basic health checks and logging

## Project Structure Context

```
apps/
├── backend/          # FastAPI backend application
│   ├── app/
│   │   ├── api/      # API route handlers
│   │   ├── core/     # Configuration and dependencies
│   │   ├── db/       # Database models and connection
│   │   ├── schemas/  # Pydantic data validation models
│   │   ├── services/ # Business logic layer
│   │   └── main.py   # FastAPI application entry point
│   ├── alembic/      # Database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
└── frontend/         # React frontend application
    ├── src/
    │   ├── api/      # Backend API clients
    │   ├── components/ # Reusable UI components
    │   ├── pages/    # Page-level components
    │   ├── store/    # Zustand state management
    │   └── styles/   # Theme and styling
    └── package.json
```

## Important Implementation Notes

- **Document Processing**: Asynchronous with status tracking (PROCESSING/COMPLETED/FAILED)
- **Authentication**: Separate login flows for admins (email/password) and employees (employee_id only)
- **Multi-tenancy**: Company-based isolation with strict filtering at database level
- **Vector Search**: Similarity search within company boundaries using pgvector
- **Error Handling**: Global FastAPI middleware for consistent error responses
- **API Documentation**: Auto-generated OpenAPI/Swagger at `/docs` endpoint