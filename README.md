# HR Internal Q&A System

A RAG-powered chatbot system for HR internal knowledge management with multi-tenant data isolation.

## Project Structure

```
hr-chatbot-system/
├── apps/
│   ├── frontend/           # React frontend application
│   └── backend/            # FastAPI backend application
├── packages/
│   └── shared-types/       # Shared TypeScript types
├── scripts/                # Project scripts
├── docs/                   # Documentation
└── IMPLEMENTATION_PLAN.md  # Detailed implementation plan
```

## Tech Stack

- **Frontend**: React + TypeScript + Vite + MUI + Zustand
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL + PGVector
- **Architecture**: Monolith in Monorepo

## Development Setup

### Prerequisites

- Node.js >= 20.0.0
- Python >= 3.11
- PostgreSQL >= 16
- Docker (optional, for containerized development)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start development servers:
   ```bash
   npm run dev
   ```

## Available Scripts

- `npm run dev` - Start both frontend and backend dev servers
- `npm run build` - Build frontend for production
- `npm run test` - Run all tests
- `npm run lint` - Lint all code
- `npm run format` - Format all code

## Documentation

See the `docs/` directory for detailed documentation:
- [Architecture Document](docs/architect.md)
- [Frontend Specification](docs/front-end-spec.md)
- [Product Requirements](docs/prd.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)