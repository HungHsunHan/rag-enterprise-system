# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive multi-tenant Enterprise RAG System built with React frontend and FastAPI backend. It provides intelligent document management and natural language query capabilities with strict company-level data isolation.

**Key Technologies:**
- Frontend: React 18 + TypeScript + Vite + Material-UI + Zustand
- Backend: FastAPI + SQLAlchemy + PostgreSQL + PGVector + Alembic
- AI/ML: OpenRouter API + Sentence Transformers + Langchain

## Development Commands

### Primary Development Commands
```bash
# Start full development environment (frontend + backend)
npm run dev

# Individual services
npm run dev:frontend    # React dev server on port 3000
npm run dev:backend     # FastAPI server on port 8000

# Build and test
npm run build           # Build frontend for production
npm run test           # Run all tests (frontend + backend)
npm run lint           # Lint all code
npm run format         # Format all code
```

### Backend-Specific Commands (from apps/backend/)
```bash
# Database migrations
python -m alembic upgrade head
python -m alembic revision --autogenerate -m "description"

# Testing with coverage
python -m pytest
python -m pytest --cov=app tests/
python -m pytest tests/test_specific.py

# Code quality
black .                 # Format code
ruff check .           # Lint code
ruff check . --fix     # Auto-fix linting issues
mypy .                 # Type checking
```

### Database Management
```bash
# Start/stop database services
docker-compose up -d postgres redis
docker-compose down

# Access PostgreSQL directly
docker-compose exec postgres psql -U postgres -d hr_chatbot

# Initialize database with dev data
docker-compose exec -T postgres psql -U postgres -d hr_chatbot < create-dev-data.sql
```

## Architecture Overview

### Multi-Tenant Design
The system implements strict multi-tenant isolation:
- **Company-scoped data**: All user queries are automatically filtered by company_id
- **Shared documents**: Special documents marked as "共同" are accessible across companies
- **Role-based access**: Admins have global access, employees are company-scoped
- **Database isolation**: All queries include company filtering at the database level

### Core Models
- `Company`: Multi-tenant organizations with UUID primary keys
- `Admin`: System administrators with global access
- `User`: Company employees with employee_id authentication
- `KnowledgeDocument`: Documents with company/shared visibility
- `DocumentChunk`: Vector embeddings with company isolation
- `LLMModel`: Dynamic AI model management

### API Structure
- `/api/v1/auth/*`: Authentication endpoints
- `/api/v1/admin/*`: Admin-only endpoints (user management, document processing)
- `/api/v1/chat`: Company-scoped RAG chat endpoint

### Frontend Architecture
- **Pages**: Route-level components in `src/pages/`
- **Components**: Reusable UI components
- **Store**: Zustand for authentication and state management
- **API**: HTTP client with automatic JWT token handling

## Key Development Patterns

### Authentication Flow
1. Admin login: email/password → JWT token with admin role
2. Employee login: employee_id only → JWT token with company context
3. All API calls include company filtering for employees

### Document Processing Workflow
1. Upload document → PENDING status
2. Admin configures chunk parameters via dialog
3. Background processing → PROCESSING status
4. Vector embeddings generated → COMPLETED status

### RAG Query Flow
1. User submits query → company context extracted from JWT
2. Vector similarity search filtered by company_id + shared documents
3. LLM generates response using company-scoped context only

## Testing Strategy

The project maintains comprehensive test coverage (46+ tests):
- **Unit Tests**: Business logic and service layer testing
- **Integration Tests**: API endpoints with database operations
- **Multi-tenant Tests**: Company isolation and shared document access
- **RAG Tests**: Query scoping and context building

Run tests with: `npm run test` (full suite) or `cd apps/backend && python -m pytest`

## Environment Setup

### Required Services
- PostgreSQL with PGVector extension
- Redis (for caching)
- Python 3.9+ environment with conda recommended
- Node.js 20+ and npm 10+

### Configuration Files
- `.env`: Backend configuration (DATABASE_URL, OPENROUTER_API_KEY, etc.)
- `docker-compose.yml`: Database services
- `create-dev-data.sql`: Development data initialization

### Development Data
- Admin: admin@dev.com / admin123
- Test employees: BRIAN001, TONY001, LISA001 (different companies)
- Sample documents and companies pre-loaded

## Common Tasks

### Adding New Features
1. Update database models in `app/db/models.py`
2. Create Alembic migration: `alembic revision --autogenerate`
3. Add Pydantic schemas in `app/schemas/`
4. Implement service layer in `app/services/`
5. Add API endpoints in `app/api/`
6. Update frontend components and API clients
7. Write comprehensive tests

### Working with Multi-Tenancy
- Always filter by company_id in database queries
- Use `get_current_user_company` dependency for company context
- Test cross-company data isolation thoroughly
- Consider shared document access patterns

### AI/ML Development
- LLM models managed dynamically via admin interface
- Embeddings use sentence-transformers models
- Vector search respects company boundaries automatically
- Test RAG responses for company-scoped accuracy

## Production Considerations

- Run migrations before deployment: `alembic upgrade head`
- Set proper CORS origins for frontend domain
- Use environment-specific configurations
- Monitor database query performance for large document sets
- Implement proper logging and error handling