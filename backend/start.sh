#!/bin/sh

echo "Waiting for database to be ready..."
while ! nc -z db 3306; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - running migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py