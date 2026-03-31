import os
import multiprocessing
from app.config import settings

# Server socket - use Render's dynamic PORT
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = settings.gunicorn_workers
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Timeout settings
timeout = settings.gunicorn_timeout
keepalive = settings.gunicorn_keepalive
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vintique"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"

# Hooks
def on_starting(server):
    server.log.info("Server is starting...")

def when_ready(server):
    server.log.info("Server is ready.")

def worker_exit(server, worker):
    server.log.info(f"Worker exited (pid: {worker.pid})")

def on_exit(server):
    server.log.info("Server is shutting down...")