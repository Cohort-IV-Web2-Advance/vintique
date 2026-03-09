#!/bin/sh

# echo "Running database migrations..."
# alembic upgrade head

# echo "Starting application..."
# exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py


#!/bin/sh
echo "Running database migrations..."

# Check if alembic_version table exists (i.e. DB has been initialized before)
TABLE_EXISTS=$(python -c "
from app.db.session import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('yes' if 'alembic_version' in inspector.get_table_names() else 'no')
")

if [ "$TABLE_EXISTS" = "no" ]; then
    echo "Fresh database detected, stamping base..."
    alembic stamp base
fi

alembic upgrade head
echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py