#!/bin/sh
set -e
echo "Running database migrations..."
alembic upgrade head #Perhaps we should use alembic upgrade head --autogenerate
echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py