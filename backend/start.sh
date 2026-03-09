#!/bin/sh

echo "Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
" 2>/dev/null && break

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Database not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES). Retrying in 2s..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Could not connect to database after $MAX_RETRIES attempts"
    exit 1
fi

echo "Database is ready!"
echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py