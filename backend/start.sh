#!/bin/sh

# echo "Running database migrations..."
# alembic upgrade head

# echo "Starting application..."
# exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py


#!/bin/sh
echo "Running database migrations..."

# Check if alembic_version table exists
TABLE_EXISTS=$(python -c "
import os
import pymysql
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'])
conn = pymysql.connect(
    host=url.hostname,
    port=url.port or 3306,
    user=url.username,
    password=url.password,
    database=url.path.lstrip('/')
)
cursor = conn.cursor()
cursor.execute(\"SHOW TABLES LIKE 'alembic_version'\")
print('yes' if cursor.fetchone() else 'no')
conn.close()
")

if [ "$TABLE_EXISTS" = "no" ]; then
    echo "Fresh database detected, stamping base..."
    alembic stamp base
fi

alembic upgrade head
echo "Starting application..."
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py