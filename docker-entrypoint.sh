#!/bin/bash
set -e

# Verify required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is required"
    exit 1
fi

# Create required directories if they don't exist
mkdir -p /app/logs
mkdir -p /app/uploads

# Set default values for optional environment variables
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-info}
export ENVIRONMENT=${ENVIRONMENT:-production}

# Run gunicorn with our configuration
exec gunicorn \
    --bind ${HOST}:${PORT} \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level ${LOG_LEVEL} \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    api:app 