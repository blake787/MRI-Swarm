# MRI-Swarm API Documentation

## Overview

The MRI-Swarm API provides endpoints for analyzing MRI images using swarm intelligence. The API is built with FastAPI and can be deployed using Gunicorn for production use.

## Running the API

### Development Mode
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
gunicorn -c gunicorn_config.py api:app
```

## API Endpoints

### 1. Analyze Single Image
- **Endpoint**: `/analyze/single`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `task` (string, required): The analysis task or clinical question
  - `additional_patient_info` (string, optional): Additional patient information
  - `image` (file, required): The MRI image file
- **Response**: JSON object containing analysis results

Example using curl:
```bash
curl -X POST "http://localhost:8000/analyze/single" \
  -H "accept: application/json" \
  -F "task=Analyze this brain MRI for any abnormalities" \
  -F "additional_patient_info=Patient age: 45, Previous conditions: None" \
  -F "image=@path/to/mri.jpg"
```

### 2. Analyze Multiple Images
- **Endpoint**: `/analyze/multiple`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `task` (string, required): The analysis task or clinical question
  - `additional_patient_info` (string, optional): Additional patient information
  - `images` (files, required): Multiple MRI image files
- **Response**: JSON object containing analysis results

Example using curl:
```bash
curl -X POST "http://localhost:8000/analyze/multiple" \
  -H "accept: application/json" \
  -F "task=Compare these MRI scans for changes" \
  -F "additional_patient_info=Follow-up scan after 6 months" \
  -F "images=@scan1.jpg" \
  -F "images=@scan2.jpg"
```

### 3. Batch Analysis
- **Endpoint**: `/analyze/batch`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `tasks` (array of strings, required): List of analysis tasks or clinical questions for each case
  - `patient_infos` (array of strings, required): List of patient information strings corresponding to each task
  - `images` (array of files, required): List of MRI image files corresponding to each task
- **Response**: Array of JSON objects containing analysis results for each case

Example using curl:
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "tasks=[\"Analyze for tumors\", \"Check for inflammation\"]" \
  -F "patient_infos=[\"Patient age: 45, History: None\", \"Patient age: 32, History: Headaches\"]" \
  -F "images=@scan1.jpg" \
  -F "images=@scan2.jpg"
```

Note: The number of tasks, patient_infos, and images must match.

### 4. Health Check
- **Endpoint**: `/health`
- **Method**: GET
- **Response**: JSON object with API health status

Example using curl:
```bash
curl "http://localhost:8000/health"
```

## API Documentation UI

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 400: Bad Request (invalid input)
- 500: Internal Server Error

## Production Deployment Notes

1. Configure CORS appropriately in `api.py`
2. Set up SSL certificates
3. Configure appropriate user/group in `gunicorn_config.py`
4. Set up proper logging rotation
5. Use environment variables for sensitive configuration 