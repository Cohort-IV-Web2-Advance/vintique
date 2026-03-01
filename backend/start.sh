#!/bin/sh

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py