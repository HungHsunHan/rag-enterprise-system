# HR Internal Q&A System 🤖

A comprehensive RAG-powered (Retrieval-Augmented Generation) HR chatbot system built for enterprise use with multi-tenant data isolation, intelligent document processing, and natural language query capabilities.

[![Built with React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](https://reactjs.org/)
[![Built with FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Built with PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2B%20PGVector-336791?logo=postgresql)](https://www.postgresql.org/)
[![AI Powered](https://img.shields.io/badge/AI-OpenRouter%20%2B%20Sentence%20Transformers-FF6B6B)](https://openrouter.ai/)

## ✨ Features

### 🔐 Multi-Tenant Authentication System
- **Admin Dashboard**: Full system administration with company management
- **Employee Access**: Company-scoped access with secure authentication
- **Role-Based Permissions**: Granular access control for different user types

### 📚 Intelligent Knowledge Management
- **Multi-Format Support**: PDF, DOCX, TXT document processing
- **Vector Embeddings**: Advanced semantic search using sentence transformers
- **Real-time Processing**: Asynchronous document processing with status tracking
- **Version Control**: Document versioning and metadata management

### 🤖 Advanced RAG System
- **Contextual Responses**: AI-powered responses based on company knowledge base
- **Free LLM Integration**: Uses OpenRouter API with free models
- **Semantic Search**: PGVector-powered similarity search for relevant context
- **Feedback Loop**: User feedback collection for continuous improvement

### 🏢 Enterprise-Ready Architecture
- **Multi-Tenant Isolation**: Strict data separation between companies
- **Scalable Design**: Monolithic architecture with clear separation of concerns
- **Security First**: JWT authentication, input validation, and secure APIs
- **Production Ready**: Comprehensive logging, error handling, and monitoring

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Node.js** >= 20.0.0 and npm >= 10.0.0
- **Python** 3.9+ (conda environment recommended)
- **Docker & Docker Compose** (for database services)
- **Git** (for version control)

### ⚡ One-Command Setup

The fastest way to get started:

```bash
# Clone and setup the entire project
git clone <your-repository-url>
cd rag-enterprise-system

# Run the automated setup script (handles everything!)
./scripts/dev-setup.sh
```

This automated script will:
- ✅ Start PostgreSQL and Redis containers
- ✅ Install all frontend and backend dependencies
- ✅ Initialize database with development data
- ✅ Create development user accounts
- ✅ Verify all services are running correctly

### 🎯 Start Development

After setup, start all services:

```bash
# Start both frontend and backend
npm run dev
```

## 📍 Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Application** | http://localhost:3000 | React frontend interface |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **API Health Check** | http://localhost:8000/health | Backend health status |
| **Admin Dashboard** | http://localhost:3000/admin | Administrative interface |

## 🔑 Development Credentials

### 👨‍💼 Admin Access (Full System Control)
```
Email: admin@dev.com
Password: admin123
```
**Capabilities**: Company management, user administration, knowledge base management, system monitoring

### 👩‍💻 Employee Access (Company-Scoped)
Choose any employee ID:
- `EMP001`, `EMP002` - **Acme Corp** employees
- `DEV001`, `TEST001` - **Tech Innovations Inc** employees

**Note**: Employee login only requires Employee ID (no password needed for development)

## 🛠 Development Commands

### Root Level Commands
```bash
# Development
npm run dev              # Start both frontend and backend
npm run dev:frontend     # Start frontend only (port 3000)  
npm run dev:backend      # Start backend only (port 8000)

# Building
npm run build            # Build frontend for production
npm run build:frontend   # Build frontend specifically

# Testing
npm run test             # Run all tests
npm run test:frontend    # Run frontend tests
npm run test:backend     # Run backend tests

# Code Quality
npm run lint             # Lint all code
npm run lint:frontend    # Lint frontend code
npm run lint:backend     # Lint backend code
npm run format           # Format all code
npm run format:frontend  # Format frontend code
npm run format:backend   # Format backend code
```

### Backend Commands (from apps/backend/)
```bash
# Database migrations
python -m alembic upgrade head                    # Apply migrations
python -m alembic revision --autogenerate -m "description"  # Create migration

# Testing
python -m pytest                                 # Run all tests
python -m pytest tests/test_specific.py         # Run specific test
python -m pytest --cov=app tests/               # Run tests with coverage

# Code quality
black .                                          # Format code
ruff check .                                    # Lint code  
ruff check . --fix                              # Fix linting issues
mypy .                                          # Type checking
```

## 🏗 Architecture Overview

### Technology Stack

**Frontend Stack:**
- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Material-UI (MUI)** for consistent, accessible UI components
- **Zustand** for lightweight state management
- **React Router** for client-side routing

**Backend Stack:**
- **FastAPI** with automatic OpenAPI documentation
- **SQLAlchemy** ORM with PostgreSQL database
- **Alembic** for database migrations
- **Pydantic** for data validation and serialization
- **JWT** authentication with role-based access

**AI/ML Stack:**
- **OpenRouter API** for LLM integration (free models available)
- **Sentence Transformers** for text embeddings
- **PGVector** for vector similarity search
- **Asyncio** for concurrent document processing

**Infrastructure:**
- **PostgreSQL** with PGVector extension for vector storage
- **Redis** for caching and session management
- **Docker Compose** for local development environment
- **Alembic** for database schema versioning

### Project Structure

```
rag-enterprise-system/
├── 📱 apps/
│   ├── frontend/                 # React frontend application
│   │   ├── src/
│   │   │   ├── api/             # Backend API clients
│   │   │   ├── components/      # Reusable UI components
│   │   │   ├── pages/           # Page-level components
│   │   │   ├── store/           # Zustand state management
│   │   │   └── styles/          # Theme and styling
│   │   └── package.json
│   └── backend/                  # FastAPI backend application
│       ├── app/
│       │   ├── api/             # API route handlers
│       │   ├── core/            # Configuration and dependencies
│       │   ├── db/              # Database models and repositories
│       │   ├── schemas/         # Pydantic data validation models
│       │   ├── services/        # Business logic layer
│       │   └── main.py          # FastAPI application entry point
│       ├── alembic/             # Database migrations
│       ├── tests/               # Backend tests
│       └── requirements.txt
├── 🐳 docker-compose.yml        # Database services
├── 📝 scripts/                  # Development setup scripts
├── 📚 docs/                     # Comprehensive documentation
├── 🔧 .env.example              # Environment variables template
└── 📊 create-dev-data.sql       # Development data initialization
```

### Database Schema

The system uses PostgreSQL with the following core tables:

| Table | Purpose | Key Features |
|-------|---------|-------------|
| `companies` | Multi-tenant organizations | UUID primary keys, company metadata |
| `admins` | System administrators | Global access, hashed passwords |
| `users` | Company employees | Company-scoped access, employee IDs |
| `knowledge_documents` | Uploaded files | Multi-format support, processing status |
| `document_chunks` | Text segments | Vector embeddings, semantic search |
| `feedback_logs` | User interactions | Q&A feedback, system improvement |

## 🧠 AI Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM API Configuration (OpenRouter)
OPENROUTER_API_KEY=your-openrouter-api-key-here
LLM_MODEL=microsoft/phi-3-mini-128k-instruct:free

# Embedding Configuration (Free Models)
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
EMBEDDING_DIMENSION=384

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_chatbot

# Security Configuration
SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
DEBUG=true
```

### Available AI Models

**Free LLM Models (via OpenRouter):**
- `microsoft/phi-3-mini-128k-instruct:free` (default - fast, efficient)
- `meta-llama/llama-3.1-8b-instruct:free` (more capable, slower)
- `mistralai/mistral-7b-instruct:free` (balanced performance)

**Embedding Models:**
- `sentence-transformers/paraphrase-MiniLM-L3-v2` (default - 384 dimensions)
- `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, good balance)
- `sentence-transformers/all-MiniLM-L12-v2` (384 dimensions, highest accuracy)

## 🗄 Database Management

### Docker Commands

```bash
# Start database services
docker-compose up -d postgres redis

# Check service status
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs redis

# Stop services
docker-compose down

# Reset database (destructive!)
docker-compose down -v && docker-compose up -d postgres redis
```

### Database Access

```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U postgres -d hr_chatbot

# Common SQL queries
SELECT * FROM companies;
SELECT * FROM users WHERE company_id = 'your-company-id';
SELECT title, status FROM knowledge_documents;
```

### Manual Database Initialization

If you need to manually initialize the database:

```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Wait for database to be ready
docker-compose exec postgres pg_isready -U postgres

# Initialize with development data
docker-compose exec -T postgres psql -U postgres -d hr_chatbot < create-dev-data.sql
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm run test

# Frontend tests only
npm run test:frontend

# Backend tests with coverage
cd apps/backend
python -m pytest --cov=app --cov-report=html tests/

# Run specific test files
python -m pytest tests/test_auth.py
python -m pytest tests/test_rag_service.py -v
```

### Test Coverage

The project maintains comprehensive test coverage:

- **Unit Tests**: Business logic, utility functions
- **Integration Tests**: API endpoints, database operations
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: Response times, concurrent users

## 🔧 Troubleshooting

### Common Issues and Solutions

**🚫 Backend won't start:**
```bash
# Check Python environment
python --version  # Should be 3.9+

# Verify dependencies
pip list | grep fastapi

# Check database connection
docker-compose ps
docker-compose logs postgres
```

**🚫 Frontend build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 20+
```

**🚫 Database connection issues:**
```bash
# Test database connectivity
docker-compose exec postgres pg_isready -U postgres

# Reset database completely
docker-compose down -v
docker-compose up -d postgres redis
# Wait 10 seconds, then run create-dev-data.sql
```

**🚫 Port conflicts:**
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Kill processes if needed
kill -9 $(lsof -ti:3000)
```

### Performance Optimization

**For Development:**
- Use `npm run dev` for hot reloading
- Enable browser dev tools for debugging
- Monitor backend logs for API performance

**For Production:**
- Build frontend with `npm run build`
- Use environment-specific configurations
- Monitor database query performance
- Implement proper logging and monitoring

## 🔒 Security Features

### Multi-Tenant Security
- **Data Isolation**: All queries filtered by `company_id`
- **Access Control**: Role-based permissions (admin vs employee)
- **Input Validation**: Comprehensive request validation using Pydantic
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: bcrypt for admin passwords
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: Sensitive data kept in environment

### Data Protection
- **No Sensitive Logging**: Passwords, API keys, and tokens never logged
- **HTTPS Ready**: SSL/TLS configuration for production
- **API Rate Limiting**: Built-in protection against abuse
- **Input Sanitization**: XSS and injection attack prevention

## 📚 Documentation

### Additional Resources

Explore the `docs/` directory for comprehensive documentation:

- **[Architecture Guide](docs/architecture.md)** - Detailed system design
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Frontend Guide](docs/frontend.md)** - Component structure and patterns
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Contributing Guide](docs/contributing.md)** - Development workflow and standards

### API Documentation

When the backend is running, visit http://localhost:8000/docs for interactive API documentation with:

- **Request/Response Examples**: Complete API schemas
- **Authentication Examples**: JWT token usage
- **Try It Out**: Interactive API testing
- **Error Responses**: Detailed error handling

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/rag-enterprise-system.git
   cd rag-enterprise-system
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-amazing-feature
   ```

3. **Set Up Development Environment**
   ```bash
   ./scripts/dev-setup.sh
   ```

4. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Test Your Changes**
   ```bash
   npm run test
   npm run lint
   npm run format
   ```

6. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   git push origin feature/your-amazing-feature
   ```

7. **Create Pull Request**
   - Describe your changes clearly
   - Include screenshots for UI changes
   - Ensure all tests pass

### Code Standards

- **TypeScript**: Use strict typing for frontend code
- **Python**: Follow PEP 8 style guidelines
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update relevant docs for changes
- **Git**: Use conventional commit messages

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🎯 Roadmap

### Upcoming Features

- [ ] **Advanced Analytics Dashboard** - Usage metrics and insights
- [ ] **Multi-Language Support** - Internationalization
- [ ] **Advanced Document Types** - Excel, PowerPoint support
- [ ] **Real-time Collaboration** - Multiple admin collaboration
- [ ] **Advanced AI Features** - Conversation memory, context awareness
- [ ] **Mobile App** - React Native companion app
- [ ] **SSO Integration** - Enterprise single sign-on
- [ ] **Advanced Search** - Full-text search with filters

### Technical Improvements

- [ ] **Microservices Architecture** - Service decomposition
- [ ] **Kubernetes Deployment** - Container orchestration
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Performance Monitoring** - APM integration
- [ ] **Caching Layer** - Redis-based response caching
- [ ] **Load Balancing** - Multi-instance deployment
- [ ] **Database Sharding** - Horizontal scaling

---

## 📞 Support

### Getting Help

- **📖 Documentation**: Check the `docs/` directory first
- **🐛 Issues**: Report bugs on GitHub Issues
- **💬 Discussions**: Join GitHub Discussions for questions
- **📧 Email**: Contact the development team

### Community

- **⭐ Star the repo** if you find it useful
- **🍴 Fork and contribute** to make it better
- **📢 Share** with your network

---

**Built with ❤️ using modern web technologies and AI innovation**