#!/bin/bash

# Vintique PostgreSQL Migration Script
# Usage: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Starting Vintique deployment with PostgreSQL..."

# Function to deploy development environment
deploy_dev() {
    echo "📦 Deploying to DEVELOPMENT environment (Local Docker PostgreSQL)"
    
    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    sudo docker compose down --volumes --remove-orphans
    
    # Start with development environment
    echo "🔧 Starting containers with PostgreSQL..."
    sudo docker compose --env-file .env.dev up -d --build
    
    # Wait for database to be ready
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    echo "🔄 Running database migrations..."
    sudo docker compose exec backend alembic upgrade head
    
    echo "✅ Development deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "🗄️  pgAdmin: http://localhost:8080 (admin@vintique.com / admin)"
}

# Function to deploy production environment
deploy_prod() {
    echo "📦 Deploying to PRODUCTION environment (Supabase)"
    
    # Validate that required environment variables are set
    if [ ! -f .env.prod ]; then
        echo "❌ .env.prod file not found!"
        echo "Please create .env.prod with your Supabase configuration."
        exit 1
    fi
    
    # Check if DATABASE_URL contains Supabase
    if ! grep -q "supabase" .env.prod; then
        echo "❌ DATABASE_URL in .env.prod doesn't appear to be a Supabase URL!"
        exit 1
    fi
    
    echo "🔧 Starting production containers with Supabase..."
    
    # For production, we might want to run without local database
    # Only backend and frontend, no local db service
    sudo docker compose -f docker-compose.yml --env-file .env.prod up -d --build backend frontend
    
    echo "✅ Production deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
}

# Main deployment logic
case $ENVIRONMENT in
    "dev")
        deploy_dev
        ;;
    "prod")
        deploy_prod
        ;;
    *)
        echo "❌ Invalid environment. Use 'dev' or 'prod'"
        echo "Usage: $0 [dev|prod]"
        exit 1
        ;;
esac

echo "🎉 Deployment completed successfully!"
