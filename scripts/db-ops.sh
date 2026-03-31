#!/bin/bash

# PostgreSQL Backup and Restore Scripts for Vintique
# Usage: ./scripts/db-ops.sh [backup|restore] [environment]

set -e

ENVIRONMENT=${2:-dev}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
CONTAINER_NAME="vintique_db"

# Create backups directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to backup database
backup_database() {
    local backup_file="$BACKUP_DIR/vintique_backup_${ENVIRONMENT}_${TIMESTAMP}.sql"
    
    print_status "Starting database backup for $ENVIRONMENT environment..."
    
    case $ENVIRONMENT in
        "dev")
            # Local PostgreSQL backup
            if sudo docker ps | grep -q $CONTAINER_NAME; then
                print_status "Creating backup: $backup_file"
                sudo docker exec $CONTAINER_NAME pg_dump -U vintique_user vintique_db > "$backup_file"
                
                # Compress the backup
                gzip "$backup_file"
                backup_file="${backup_file}.gz"
                
                print_status "Backup completed: $backup_file"
                print_status "Backup size: $(du -h "$backup_file" | cut -f1)"
            else
                print_error "Database container $CONTAINER_NAME is not running!"
                exit 1
            fi
            ;;
        "prod")
            # Supabase backup (requires pg_dump with connection string)
            if [ -f .env.prod ]; then
                source .env.prod
                print_status "Creating Supabase backup: $backup_file"
                
                # Extract connection details from DATABASE_URL
                # Format: postgresql+psycopg2://user:password@host:port/db?sslmode=require
                DB_URL=$(echo $DATABASE_URL | sed 's/postgresql+psycopg2:\/\///g' | sed 's/\?.*$//')
                
                pg_dump "$DB_URL" > "$backup_file"
                gzip "$backup_file"
                backup_file="${backup_file}.gz"
                
                print_status "Supabase backup completed: $backup_file"
                print_status "Backup size: $(du -h "$backup_file" | cut -f1)"
            else
                print_error ".env.prod file not found!"
                exit 1
            fi
            ;;
        *)
            print_error "Invalid environment. Use 'dev' or 'prod'"
            exit 1
            ;;
    esac
    
    # Keep only last 5 backups
    print_status "Cleaning up old backups (keeping last 5)..."
    cd $BACKUP_DIR
    ls -t vintique_backup_${ENVIRONMENT}_*.sql.gz | tail -n +6 | xargs -r rm
    cd - > /dev/null
}

# Function to restore database
restore_database() {
    local latest_backup=$(ls -t $BACKUP_DIR/vintique_backup_${ENVIRONMENT}_*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "$latest_backup" ]; then
        print_error "No backup found for $ENVIRONMENT environment!"
        exit 1
    fi
    
    print_warning "This will REPLACE the current database in $ENVIRONMENT environment!"
    print_warning "Backup to restore: $latest_backup"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled."
        exit 0
    fi
    
    print_status "Starting database restore for $ENVIRONMENT environment..."
    
    case $ENVIRONMENT in
        "dev")
            # Local PostgreSQL restore
            if sudo docker ps | grep -q $CONTAINER_NAME; then
                print_status "Restoring from: $latest_backup"
                
                # Decompress and restore
                gunzip -c "$latest_backup" | sudo docker exec -i $CONTAINER_NAME psql -U vintique_user -d vintique_db
                
                print_status "Database restored successfully!"
            else
                print_error "Database container $CONTAINER_NAME is not running!"
                exit 1
            fi
            ;;
        "prod")
            # Supabase restore
            if [ -f .env.prod ]; then
                source .env.prod
                print_status "Restoring Supabase from: $latest_backup"
                
                # Extract connection details
                DB_URL=$(echo $DATABASE_URL | sed 's/postgresql+psycopg2:\/\///g' | sed 's/\?.*$//')
                
                gunzip -c "$latest_backup" | psql "$DB_URL"
                
                print_status "Supabase database restored successfully!"
            else
                print_error ".env.prod file not found!"
                exit 1
            fi
            ;;
        *)
            print_error "Invalid environment. Use 'dev' or 'prod'"
            exit 1
            ;;
    esac
}

# Function to list backups
list_backups() {
    print_status "Available backups for $ENVIRONMENT environment:"
    if ls $BACKUP_DIR/vintique_backup_${ENVIRONMENT}_*.sql.gz 1> /dev/null 2>&1; then
        ls -lh $BACKUP_DIR/vintique_backup_${ENVIRONMENT}_*.sql.gz | awk '{print $9, $5}'
    else
        print_warning "No backups found for $ENVIRONMENT environment."
    fi
}

# Function to show help
show_help() {
    echo "Vintique PostgreSQL Database Operations"
    echo ""
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo ""
    echo "Commands:"
    echo "  backup   [dev|prod]  Create database backup"
    echo "  restore  [dev|prod]  Restore database from latest backup"
    echo "  list     [dev|prod]  List available backups"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup dev        # Backup development database"
    echo "  $0 restore prod      # Restore production database"
    echo "  $0 list dev          # List development backups"
}

# Main execution
case $1 in
    "backup")
        backup_database
        ;;
    "restore")
        restore_database
        ;;
    "list")
        list_backups
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Invalid command!"
        show_help
        exit 1
        ;;
esac
