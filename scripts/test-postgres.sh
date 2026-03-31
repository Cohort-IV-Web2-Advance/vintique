#!/bin/bash

# Comprehensive PostgreSQL Testing Script
# Tests database connectivity, CRUD operations, and performance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  PostgreSQL Migration Test Suite${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test 1: Database Connectivity
test_database_connectivity() {
    print_test "Testing database connectivity..."
    
    if sudo docker compose exec -T backend python -c "
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text('SELECT 1 as test'))
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
finally:
    db.close()
" > /dev/null 2>&1; then
        print_pass "Database connectivity test passed"
        return 0
    else
        print_fail "Database connectivity test failed"
        return 1
    fi
}

# Test 2: Table Creation
test_table_creation() {
    print_test "Testing table creation..."
    
    if sudo docker compose exec -T backend python -c "
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    tables = db.execute(text(\"\"\"
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    \"\"\"))
    table_names = [row[0] for row in tables]
    expected_tables = {'users', 'accounts', 'products', 'cart', 'orders', 'transactions', 'guests', 'alembic_version'}
    
    missing_tables = expected_tables - set(table_names)
    if missing_tables:
        print(f'❌ Missing tables: {missing_tables}')
        exit(1)
    else:
        print('✅ All required tables exist')
except Exception as e:
    print(f'❌ Table check failed: {e}')
    exit(1)
finally:
    db.close()
" > /dev/null 2>&1; then
        print_pass "Table creation test passed"
        return 0
    else
        print_fail "Table creation test failed"
        return 1
    fi
}

# Test 3: CRUD Operations
test_crud_operations() {
    print_test "Testing CRUD operations..."
    
    if sudo docker compose exec -T backend python -c "
import sys
sys.path.append('/app')

from app.database import SessionLocal
from app.models import Product, User, Account
from app.core.auth import get_password_hash
from decimal import Decimal
from datetime import datetime

db = SessionLocal()
try:
    # CREATE - Test User Creation
    test_user = User(
        email='test@example.com',
        username='test_user',
        password=get_password_hash('test123'),
        is_admin=False,
        status='active'
    )
    db.add(test_user)
    db.flush()
    user_id = test_user.id
    
    # CREATE - Test Product Creation
    test_product = Product(
        name='Test Product',
        description='Test Description',
        price=Decimal('99.99'),
        stock_quantity=10
    )
    db.add(test_product)
    db.flush()
    product_id = test_product.id
    
    # READ - Test User Retrieval
    retrieved_user = db.query(User).filter(User.id == user_id).first()
    if not retrieved_user or retrieved_user.email != 'test@example.com':
        print('❌ User retrieval failed')
        exit(1)
    
    # READ - Test Product Retrieval
    retrieved_product = db.query(Product).filter(Product.id == product_id).first()
    if not retrieved_product or retrieved_product.name != 'Test Product':
        print('❌ Product retrieval failed')
        exit(1)
    
    # UPDATE - Test User Update
    retrieved_user.shipping_address = '123 Test St'
    db.commit()
    
    updated_user = db.query(User).filter(User.id == user_id).first()
    if updated_user.shipping_address != '123 Test St':
        print('❌ User update failed')
        exit(1)
    
    # DELETE - Test Cleanup
    db.delete(retrieved_user)
    db.delete(retrieved_product)
    db.commit()
    
    # Verify deletion
    deleted_user = db.query(User).filter(User.id == user_id).first()
    deleted_product = db.query(Product).filter(Product.id == product_id).first()
    
    if deleted_user is not None or deleted_product is not None:
        print('❌ Record deletion failed')
        exit(1)
    
    print('✅ CRUD operations successful')
    
except Exception as e:
    print(f'❌ CRUD test failed: {e}')
    db.rollback()
    exit(1)
finally:
    db.close()
" > /dev/null 2>&1; then
        print_pass "CRUD operations test passed"
        return 0
    else
        print_fail "CRUD operations test failed"
        return 1
    fi
}

# Test 4: API Endpoints
test_api_endpoints() {
    print_test "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_pass "Health endpoint test passed"
    else
        print_fail "Health endpoint test failed"
        return 1
    fi
    
    # Test docs endpoint
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        print_pass "API docs endpoint test passed"
    else
        print_fail "API docs endpoint test failed"
        return 1
    fi
}

# Test 5: Migration System
test_migration_system() {
    print_test "Testing migration system..."
    
    if sudo docker compose exec -T backend alembic current > /dev/null 2>&1; then
        print_pass "Migration system test passed"
        return 0
    else
        print_fail "Migration system test failed"
        return 1
    fi
}

# Test 6: Database Performance
test_database_performance() {
    print_test "Testing database performance..."
    
    if sudo docker compose exec -T backend python -c "
from app.database import SessionLocal
from sqlalchemy import text
import time

db = SessionLocal()
try:
    # Test query performance
    start_time = time.time()
    
    # Simple count query
    result = db.execute(text('SELECT COUNT(*) FROM users'))
    user_count = result.scalar()
    
    # Join query performance
    result = db.execute(text('''
        SELECT u.username, a.balance 
        FROM users u 
        LEFT JOIN accounts a ON u.id = a.user_id 
        LIMIT 10
    '''))
    
    query_time = time.time() - start_time
    
    if query_time > 2.0:  # Queries should complete within 2 seconds
        print(f'❌ Query performance too slow: {query_time:.2f}s')
        exit(1)
    
    print(f'✅ Database performance OK ({query_time:.2f}s)')
    
except Exception as e:
    print(f'❌ Performance test failed: {e}')
    exit(1)
finally:
    db.close()
" > /dev/null 2>&1; then
        print_pass "Database performance test passed"
        return 0
    else
        print_fail "Database performance test failed"
        return 1
    fi
}

# Test 7: Container Health
test_container_health() {
    print_test "Testing container health..."
    
    # Check if all containers are running and healthy
    containers=("vintique_db" "vintique_backend" "vintique_frontend")
    
    for container in "${containers[@]}"; do
        if sudo docker ps --filter "name=$container" --filter "status=running" --format "{{.Names}}" | grep -q "$container"; then
            print_pass "Container $container is running"
        else
            print_fail "Container $container is not running"
            return 1
        fi
    done
    
    return 0
}

# Main test execution
main() {
    print_header
    print_info "Starting PostgreSQL migration test suite..."
    print_info "Environment: Development"
    echo
    
    tests=(
        "test_container_health"
        "test_database_connectivity"
        "test_table_creation"
        "test_crud_operations"
        "test_api_endpoints"
        "test_migration_system"
        "test_database_performance"
    )
    
    total_tests=${#tests[@]}
    passed_tests=0
    failed_tests=0
    
    for test in "${tests[@]}"; do
        if $test; then
            ((passed_tests++))
        else
            ((failed_tests++))
        fi
        echo
    done
    
    # Test Summary
    print_header
    print_info "Test Results Summary:"
    print_info "Total Tests: $total_tests"
    print_pass "Passed: $passed_tests"
    
    if [ $failed_tests -gt 0 ]; then
        print_fail "Failed: $failed_tests"
        echo
        print_fail "Some tests failed. Please check the configuration and try again."
        exit 1
    else
        print_pass "All tests passed! PostgreSQL migration is working correctly."
        echo
        print_info "Your Vintique application is ready for production deployment."
    fi
}

# Run main function
main "$@"
