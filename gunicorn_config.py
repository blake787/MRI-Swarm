import multiprocessing
import os

# Server socket
bind = os.getenv("BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
workers = os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 2

# Process naming
proc_name = "mri-swarm-api"
pythonpath = "."

# Logging
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "info"

# Process management
daemon = False
pidfile = "mri-swarm-api.pid"

# SSL (uncomment and configure for HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Server mechanics
user = None  # Set appropriate user in production
group = None  # Set appropriate group in production
tmp_upload_dir = None
spew = False


# Server hooks
def on_starting(server):
    """
    Server initialization.
    """
    pass


def on_reload(server):
    """
    Code reload (for development).
    """
    pass


def when_ready(server):
    """
    Server is ready to accept requests.
    """
    pass


def on_exit(server):
    """
    Server cleanup before exit.
    """
    pass
