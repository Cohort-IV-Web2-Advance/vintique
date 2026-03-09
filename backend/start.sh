#!/bin/sh

# echo "Running database migrations..."
# alembic upgrade head

# echo "Starting application..."
# exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py


#!/bin/sh
# echo "Running database migrations..."

# # Check if alembic_version table exists
# TABLE_EXISTS=$(python -c "
# import os
# import pymysql
# from urllib.parse import urlparse

# url = urlparse(os.environ['DATABASE_URL'])
# conn = pymysql.connect(
#     host=url.hostname,
#     port=url.port or 3306,
#     user=url.username,
#     password=url.password,
#     database=url.path.lstrip('/')
# )
# cursor = conn.cursor()
# cursor.execute(\"SHOW TABLES LIKE 'alembic_version'\")
# print('yes' if cursor.fetchone() else 'no')
# conn.close()
# ")

# if [ "$TABLE_EXISTS" = "no" ]; then
#     echo "Fresh database detected, stamping base..."
#     alembic stamp base
# fi

# alembic upgrade head
# echo "Starting application..."
# exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py


#!/bin/sh

echo "DB Host: $(python -c "import os; from urllib.parse import urlparse; u=urlparse(os.environ['DATABASE_URL'].replace('mysql+pymysql://','mysql://')); print(u.hostname, u.port)")"
echo "Running database migrations..."

# Wait for database to be ready
echo "Waiting for database..."
python -c "
import os, time, pymysql
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'].replace('mysql+pymysql://', 'mysql://'))

for i in range(30):
    try:
        conn = pymysql.connect(
            host=url.hostname,
            port=url.port or 3306,
            user=url.username,
            password=url.password,
            database=url.path.lstrip('/')
        )
        conn.close()
        print('Database is ready!')
        break
    except Exception as e:
        print(f'Attempt {i+1}/30: DB not ready yet... {e}')
        time.sleep(2)
else:
    print('Database never became ready, exiting')
    exit(1)
"

# Stamp base if fresh DB
TABLE_EXISTS=$(python -c "
import os, pymysql
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'].replace('mysql+pymysql://', 'mysql://'))
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