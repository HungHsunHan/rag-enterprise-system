# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Project Setup
```bash
# Start development environment (databases + install deps + init data)
./scripts/dev-setup.sh

# Start both frontend and backend
npm run dev

# Start services individually  
npm run dev:frontend    # React frontend on port 3000
npm run dev:backend     # FastAPI backend on port 8000
```

### Development Workflow
```bash
# Building
npm run build           # Build frontend for production

# Testing
npm run test            # Run all tests (frontend + backend)
npm run test:frontend   # Run frontend tests (vitest)
npm run test:backend    # Run backend tests (pytest)

# Code Quality
npm run lint            # Lint all code
npm run format          # Format all code
npm run lint:frontend   # ESLint frontend
npm run lint:backend    # Ruff backend  
npm run format:frontend # Prettier frontend
npm run format:backend  # Black + Ruff backend
```

### Backend-Specific Commands (from apps/backend/)
```bash
# Database migrations
python -m alembic upgrade head
python -m alembic revision --autogenerate -m "description"

# Testing with coverage
python -m pytest --cov=app --cov-report=html tests/
python -m pytest tests/test_specific.py     # Run specific test
python -m pytest -v                         # Verbose output

# Code quality
black .                 # Format code
ruff check .            # Lint code
ruff check . --fix      # Auto-fix linting issues
mypy .                  # Type checking
```

### Database Management
```bash
# Start/stop database services
docker-compose up -d postgres redis
docker-compose down

# Check service status
docker-compose ps
docker-compose logs postgres

# Database access
docker-compose exec postgres psql -U postgres -d hr_chatbot

# Reset database (destructive!)
docker-compose down -v && docker-compose up -d postgres redis
```

## Architecture Overview

### Technology Stack
**Frontend**: React 18 + TypeScript + Vite + Material-UI + Zustand + React Router
**Backend**: FastAPI + SQLAlchemy + Alembic + Pydantic + JWT authentication  
**Database**: PostgreSQL with PGVector extension + Redis for caching
**AI/ML**: OpenRouter API + Sentence Transformers + PGVector similarity search

### Monorepo Structure
```
apps/
├── frontend/           # React TypeScript application
│   ├── src/api/       # Backend API clients (auth, admin, user)
│   ├── src/components/# Reusable UI components  
│   ├── src/pages/     # Page components (Login, Chat, Admin)
│   ├── src/store/     # Zustand state management
│   └── src/styles/    # MUI theme configuration
└── backend/           # FastAPI Python application
    ├── app/api/       # API route handlers (auth, chat, admin)
    ├── app/core/      # Configuration and security
    ├── app/db/        # SQLAlchemy models and database
    ├── app/schemas/   # Pydantic validation models
    ├── app/services/  # Business logic layer
    ├── alembic/       # Database migrations
    └── tests/         # Backend tests
```

### Multi-Tenant Architecture
- **Data Isolation**: All queries filtered by `company_id`
- **Admin Access**: Full system administration (companies, users, documents)
- **Employee Access**: Company-scoped access with employee ID authentication
- **Security**: JWT tokens, bcrypt hashing, input validation, SQL injection prevention

### Key Services
- **RAG Service** (`app/services/rag_service.py`): Core Q&A engine with vector similarity search
- **Document Service** (`app/services/document_service.py`): File upload, processing, and vectorization
- **Auth Service** (`app/services/auth_service.py`): JWT authentication for admins and employees
- **Company Service** (`app/services/company_service.py`): Multi-tenant company management

## Development Guidelines

### Database Schema
Core tables: `companies`, `admins`, `users`, `knowledge_documents`, `document_chunks`, `feedback_logs`
- Uses UUID primary keys for companies
- PGVector extension for document embeddings (384 dimensions)
- Multi-tenant isolation via company_id foreign keys

### Authentication Flow
- **Admin Login**: Email + password → JWT token with admin privileges
- **Employee Login**: Employee ID only → JWT token scoped to company
- **JWT Tokens**: Include user_id, company_id, is_admin claims
- **Protected Routes**: All API endpoints except auth require valid JWT

### Frontend State Management
- **Zustand Store** (`src/store/authStore.ts`): Centralized auth state with persistence
- **API Clients**: Axios-based with automatic JWT token injection
- **Error Handling**: Automatic token refresh and logout on 401 responses

### Testing Strategy
- **Backend**: Pytest with fixtures for database isolation between tests
- **Frontend**: Vitest for unit tests, Playwright for e2e tests
- **Coverage**: Maintain >80% test coverage for business logic
- **Integration**: Test multi-tenant data isolation and auth flows

### File Processing Pipeline
1. Upload via multipart form to `/api/documents/upload`
2. Extract text from PDF/DOCX/TXT using pypdf/python-docx
3. Split text into chunks with overlapping windows
4. Generate embeddings using sentence-transformers
5. Store vectors in PGVector with company isolation
6. Enable semantic search via cosine similarity

### RAG Q&A Flow
1. Employee question → vector embedding
2. Similarity search in company-scoped document_chunks
3. Retrieve top K relevant chunks as context
4. Construct prompt with context + question
5. Send to OpenRouter LLM API (free models available)
6. Return generated answer to frontend

## Environment Configuration

### Required Environment Variables (.env)
```bash
# LLM Configuration (OpenRouter)
OPENROUTER_API_KEY=your-openrouter-api-key
LLM_MODEL=microsoft/phi-3-mini-128k-instruct:free

# Embedding Configuration  
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
EMBEDDING_DIMENSION=384

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_chatbot

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Development Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

### Development Credentials
**Admin**: `admin@dev.com` / `admin123`
**Employees**: Use employee IDs like `EMP001`, `EMP002`, `DEV001`, `TEST001`

## Common Issues and Solutions

### Backend Won't Start
```bash
# Check Python environment (requires 3.9+)
python --version
pip list | grep fastapi

# Verify database connection
docker-compose ps
docker-compose logs postgres
```

### Frontend Build Errors
```bash
# Clear cache and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node.js version (requires 20+)
node --version
```

### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec postgres pg_isready -U postgres

# Reset database completely
docker-compose down -v
docker-compose up -d postgres redis
# Wait 10 seconds, then initialize with dev data
```

### Port Conflicts
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Kill processes if needed
kill -9 $(lsof -ti:3000)
```

## Implementation Notes

The system is currently in active development with comprehensive testing and monitoring features implemented. The codebase follows clean architecture principles with clear separation between API routes, business logic services, and data access layers.

When making changes:
1. Follow existing patterns in the codebase
2. Maintain multi-tenant data isolation
3. Update tests for new functionality
4. Run linting and formatting before committing
5. Test both admin and employee user flows