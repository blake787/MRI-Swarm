# Docker Setup Guide

This guide explains how to use Docker to run MRI Swarm in a containerized environment.

## Prerequisites

- Docker installed on your system
- Git repository cloned locally

## Environment Variables

The Dockerfile supports the following environment variables:

- `PORT`: Server port (default: 8000)
- `HOST`: Host address (default: 0.0.0.0)
- `WORKERS`: Number of Gunicorn workers (default: 4)
- `LOG_LEVEL`: Logging level (default: info)
- `MAX_LOG_FILE_SIZE`: Maximum log file size in bytes (default: 10MB)
- `LOG_BACKUP_COUNT`: Number of log backups to keep (default: 5)
- `ENVIRONMENT`: Deployment environment (default: production)

## Building the Docker Image

From the root directory of the project, run:

```bash
docker build -t mri-swarm .
```

## Running the Container

### Basic Usage

```bash
docker run -p 8000:8000 mri-swarm
```

### With Custom Environment Variables

```bash
docker run -p 8000:8000 \
  -e PORT=8080 \
  -e WORKERS=2 \
  -e LOG_LEVEL=debug \
  mri-swarm
```

### With Volume Mounts for Logs and Uploads

```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/uploads:/app/uploads \
  mri-swarm
```

## Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  mri-swarm:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    environment:
      - PORT=8000
      - WORKERS=4
      - LOG_LEVEL=info
```

Then run:

```bash
docker-compose up -d
```

## Security Considerations

- The container runs as a non-root user `mriswarm` for enhanced security
- Sensitive data should be passed through environment variables or secure secrets management
- Ensure proper file permissions when mounting volumes

## Troubleshooting

1. **Container fails to start**:
   - Check logs: `docker logs <container_id>`
   - Verify environment variables
   - Ensure required ports are available

2. **Permission issues**:
   - Check volume mount permissions
   - Verify user/group IDs match between host and container

3. **Performance issues**:
   - Adjust number of workers based on host resources
   - Monitor container resource usage with `docker stats`

## Production Deployment

For production deployments:

1. Set appropriate environment variables
2. Use proper logging configuration
3. Implement health checks
4. Set up monitoring
5. Use container orchestration (e.g., Kubernetes)

## Development

For development purposes, you can use:

```bash
docker run -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e LOG_LEVEL=debug \
  -v $(pwd):/app \
  mri-swarm
```

This mounts the current directory into the container for live code updates. 