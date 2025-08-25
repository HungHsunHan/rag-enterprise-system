# RAG Enterprise System - Deployment Guide

## For Colleagues/End Users

This guide helps you deploy the RAG Enterprise System using pre-built Docker images from Docker Hub.

## Prerequisites

- Docker & Docker Compose installed
- Internet connection to download images
- Minimum 4GB RAM, 2GB free disk space

## Quick Deployment Steps

### 1. Get Deployment Files
Download these files from the project:
- `docker-compose.deploy.yml` 
- `.env.production` (copy to `.env`)

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production .env

# Edit with your values
nano .env
```

**Required variables in `.env`:**
```bash
# REQUIRED - Get free key from https://openrouter.ai
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Security - Change these in production!
SECRET_KEY=your-secure-jwt-secret-key
POSTGRES_PASSWORD=your-secure-db-password  
REDIS_PASSWORD=your-secure-redis-password

# Optional customization
LLM_MODEL=openai/gpt-4o-mini
```

### 3. Deploy Application
```bash
# Start all services (downloads images automatically)
docker-compose -f docker-compose.deploy.yml up -d

# Check status
docker-compose -f docker-compose.deploy.yml ps

# View logs
docker-compose -f docker-compose.deploy.yml logs -f
```

## Access Points

After successful deployment:

- **Frontend Application**: http://localhost:4000
- **Backend API**: http://localhost:9000  
- **API Documentation**: http://localhost:9000/docs

## Image Download Process

Docker will automatically download these images:

✅ **Official Images** (public, always available):
- `pgvector/pgvector:pg16` (~464MB) - PostgreSQL with vector support
- `redis:7-alpine` (~42MB) - Redis cache

✅ **Custom Images** (from hunghsun's Docker Hub):
- `hunghsun/rag-enterprise-backend:latest` (~1.5GB) - FastAPI backend
- `hunghsun/rag-enterprise-frontend:latest` (~61MB) - React frontend

## Management Commands

```bash
# Stop all services
docker-compose -f docker-compose.deploy.yml down

# Update to latest images
docker-compose -f docker-compose.deploy.yml pull
docker-compose -f docker-compose.deploy.yml up -d

# Check service health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Remove everything (including data)
docker-compose -f docker-compose.deploy.yml down -v
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :4000
   # Kill the process or change ports in docker-compose.deploy.yml
   ```

2. **Images not found**
   ```bash
   # Manually pull images
   docker pull hunghsun/rag-enterprise-backend:latest
   docker pull hunghsun/rag-enterprise-frontend:latest
   ```

3. **Health check failing**
   ```bash
   # Check individual service logs
   docker logs rag_backend_prod
   docker logs rag_frontend_prod
   ```

### Verification Steps

1. **Check all containers are healthy**:
   ```bash
   docker ps
   # All should show "healthy" status
   ```

2. **Test API connectivity**:
   ```bash
   curl http://localhost:9000/health
   # Should return: {"status": "healthy"}
   ```

3. **Test frontend**:
   Open http://localhost:4000 in browser

## Data Persistence

Your data is stored in Docker volumes:
- Database: `rag_postgres_prod_data`
- Cache: `rag_redis_prod_data`  
- Logs: `rag_backend_logs`
- Uploads: `rag_backend_uploads`

Data persists between container restarts but is removed with `docker-compose down -v`.

## Production Considerations

- Change default passwords in `.env`
- Setup SSL/TLS with reverse proxy (nginx/traefik)
- Configure domain names
- Setup monitoring and backups
- Review security settings

## Support

If you encounter issues:
1. Check the logs: `docker-compose -f docker-compose.deploy.yml logs`
2. Verify environment variables in `.env`
3. Ensure all required ports are available
4. Contact the development team