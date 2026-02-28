#!/bin/bash

# Vintique E-commerce Deployment Script
# Usage: ./scripts/deploy.sh [development|production]

set -e

ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"

echo "🚀 Deploying Vintique E-commerce in $ENVIRONMENT mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Set compose file based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo "🔧 Using development configuration..."
elif [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🏭 Using production configuration..."
else
    echo "❌ Invalid environment. Use 'development' or 'production'."
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f $COMPOSE_FILE down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f $COMPOSE_FILE up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f $COMPOSE_FILE exec backend alembic upgrade head

# Check service health
echo "🔍 Checking service health..."
docker-compose -f $COMPOSE_FILE ps

# Show logs
echo "📋 Showing recent logs..."
docker-compose -f $COMPOSE_FILE logs --tail=20

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🗃️ phpMyAdmin: http://localhost:8080"
fi

echo "🎉 Vintique is now running!"
