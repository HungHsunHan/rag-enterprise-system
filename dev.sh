#!/bin/bash

# Start PostgreSQL and Redis containers
echo "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 3

# Check if services are healthy
echo "Checking service status..."
docker-compose ps postgres redis

# Start the development servers
echo "Starting development servers..."
npm run dev