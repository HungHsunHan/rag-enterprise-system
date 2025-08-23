# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Start all services
npm run dev                    # Both frontend (3000) and backend (8000)
npm run dev:frontend           # Frontend only
npm run dev:backend            # Backend only

# One-time setup
./scripts/dev-setup.sh         # Automated environment setup
```

### Testing
```bash
# Run all tests
npm run test                   # Both frontend and backend tests
npm run test:frontend          # Frontend tests only
npm run test:backend           # Backend tests with pytest

# Backend testing (from apps/backend/)
python -m pytest              # All tests
python -m pytest --cov=app    # With coverage
python -m pytest tests/test_specific.py  # Specific test file
```

### Code Quality
```bash
# Lint and format all code
npm run lint                   # Both frontend and backend
npm run format                 # Format all code

# Backend specific (from apps/backend/)
ruff check .                   # Lint
ruff check . --fix             # Auto-fix issues
black .                        # Format code
mypy .                         # Type check
```

### Database
```bash
# Docker database services
docker-compose up -d postgres redis      # Start services
docker-compose ps                         # Check status
docker-compose logs postgres              # View logs

# Database migrations (from apps/backend/)
python -m alembic upgrade head                           # Apply migrations
python -m alembic revision --autogenerate -m "message"  # Create migration

# Direct database access
docker-compose exec postgres psql -U postgres -d hr_chatbot
```

## Architecture Overview

This is a **multi-tenant RAG enterprise system** with strict company-level data isolation:

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite + MUI + Zustand
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + PGVector
- **AI/ML**: OpenRouter API + Sentence Transformers + RAG
- **Infrastructure**: Docker Compose for local development

### Key Components

**Monorepo Structure**:
```
apps/
├── frontend/          # React TypeScript app
│   ├── src/api/      # Backend API clients
│   ├── src/pages/    # Page components (admin/*, chat, login)
│   └── src/store/    # Zustand state management
└── backend/           # FastAPI Python app
    ├── app/api/      # Route handlers (auth, admin, chat)
    ├── app/services/ # Business logic layer
    └── tests/        # 46+ unit tests with >90% coverage
```

**Multi-Tenant Architecture**:
- **Companies**: UUID-based tenant isolation
- **Users**: Employee ID authentication, company-scoped access
- **Admins**: Global system administrators with full access
- **Documents**: Company-private or shared (共同) across all companies
- **RAG System**: Automatic company filtering + shared content inclusion

### Database Schema
- `companies` - Multi-tenant organizations
- `admins` - System administrators  
- `users` - Company employees with names and employee IDs
- `knowledge_documents` - Uploaded files with shared/private classification
- `document_chunks` - Text segments with vector embeddings
- `llm_models` - Dynamic LLM model management
- `feedback_logs` - User interaction tracking

### Authentication System
- **Admin Auth**: Email/password with JWT tokens
- **Employee Auth**: Employee ID only (development mode)
- **Company Isolation**: All queries automatically filtered by company_id
- **Shared Content**: Documents marked as 共同 accessible to all companies

## AI/ML Configuration

### Environment Variables (.env)
```bash
# LLM Configuration
OPENROUTER_API_KEY=your-key-here
LLM_MODEL=microsoft/phi-3-mini-128k-instruct:free

# Embeddings
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
EMBEDDING_DIMENSION=384

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_chatbot
```

### Document Processing Workflow
1. **Upload**: Multi-format support (.pdf, .docx, .txt)
2. **Processing**: Two-phase with configurable chunk size/overlap
3. **Vectorization**: Sentence Transformers → PGVector storage
4. **Company Scoping**: Automatic isolation + shared content support

### RAG Query Flow
1. **Authentication**: Verify user's company context
2. **Query Vectorization**: Convert question to embeddings
3. **Similarity Search**: Company-scoped + shared documents
4. **Context Assembly**: Build prompt with relevant chunks
5. **LLM Generation**: OpenRouter API call with context
6. **Response**: Return answer with source tracking

## Development Guidelines

### Critical Security Patterns
- **Never bypass company isolation**: All database queries must include company_id filtering
- **Shared documents**: Use explicit shared=True for cross-company content
- **Multi-tenant testing**: Always test with multiple companies in database

### Backend Service Layer
- `auth_service.py` - JWT and company authentication
- `rag_service.py` - Core RAG logic with company scoping
- `document_service.py` - File processing and storage
- `company_service.py` - Multi-tenant company management
- `user_service.py` - Employee management with company association

### Frontend State Management
- `authStore.ts` - Zustand store for authentication state
- JWT token persistence in localStorage with automatic refresh
- Company context maintained throughout user session

### Testing Strategy
- **46+ unit tests** with >90% coverage
- **Multi-tenant isolation testing** - Critical for security
- **RAG functionality tests** - Query scoping and shared content
- **Document workflow tests** - Upload, processing, status tracking
- **Admin API tests** - Company and user management

## Common Development Tasks

### Adding New API Endpoint
1. Define route in `apps/backend/app/api/`
2. Create Pydantic schemas in `apps/backend/app/schemas/`
3. Implement service logic with company isolation
4. Add comprehensive tests in `apps/backend/tests/`
5. Create frontend API client in `apps/frontend/src/api/`

### Database Schema Changes
1. Create Alembic migration: `alembic revision --autogenerate -m "description"`
2. Update SQLAlchemy models in `apps/backend/app/db/models.py`
3. Update Pydantic schemas if needed
4. Test migration: `alembic upgrade head`

### Frontend Component Development
1. Follow MUI design system patterns
2. Use Zustand for state management
3. Implement proper error handling and loading states
4. Ensure responsive design for admin interfaces

## Production Considerations

### Security Requirements
- Change default SECRET_KEY in production
- Implement proper employee authentication (not just employee ID)
- Enable HTTPS and secure headers
- Regular security audits for multi-tenant isolation

### Performance Optimization  
- PGVector index optimization for large document sets
- Redis caching for frequently accessed data
- Connection pooling for database connections
- Batch processing for document uploads

### Deployment Requirements
- PostgreSQL with PGVector extension
- Redis for caching and sessions
- Environment-specific configuration
- Health check endpoints for monitoring