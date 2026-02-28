# Gunicorn configuration file
import multiprocessing
import os
from app.config import settings

# Server socket
bind = "0.0.0.0:8000"
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
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Worker process settings
max_requests = 1000
max_requests_jitter = 50
preload_app = True
lazy_apps = False

# Monitoring
statsd_host = None
statsd_prefix = ""

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Server is starting...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Server is reloading...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready.")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"Worker initialized (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker exited (pid: {worker.pid})")

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Child worker exited (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("Server is shutting down...")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker aborted (SIGABRT received)")

# Environment variables
raw_env = [
    f"ENVIRONMENT={settings.environment}",
    f"DATABASE_URL={settings.database_url}",
    f"JWT_SECRET_KEY={settings.jwt_secret_key}",
    f"CLOUDINARY_CLOUD_NAME={settings.cloudinary_cloud_name}",
    f"CLOUDINARY_API_KEY={settings.cloudinary_api_key}",
    f"CLOUDINARY_API_SECRET={settings.cloudinary_api_secret}",
]
