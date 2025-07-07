FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=4 \
    LOG_LEVEL=info \
    MAX_LOG_FILE_SIZE=10485760 \
    LOG_BACKUP_COUNT=5 \
    ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads \
    && chmod -R 755 /app/logs /app/uploads

# Expose port
EXPOSE ${PORT}

# Create non-root user
RUN useradd -m -u 1000 mriswarm \
    && chown -R mriswarm:mriswarm /app
USER mriswarm

# Set up entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Run the application
ENTRYPOINT ["docker-entrypoint.sh"]
