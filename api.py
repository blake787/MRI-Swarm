import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import aiofiles
import uvicorn
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from mri_swarm.main import mri_swarm, batched_mri_swarm
from loguru import logger

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="MRI-Swarm API",
    description="API for MRI analysis using swarm intelligence",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MRIAnalysisRequest(BaseModel):
    task: str = Field(
        ..., description="The analysis task or clinical question to be addressed"
    )
    additional_patient_info: Optional[str] = Field(
        None, description="Additional patient information"
    )


class ErrorResponse(BaseModel):
    detail: str


class BatchMRIRequest(BaseModel):
    tasks: List[str] = Field(
        ..., description="List of analysis tasks or clinical questions for each case"
    )
    patient_infos: List[str] = Field(
        ...,
        description="List of patient information strings corresponding to each task",
    )


async def save_upload_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file and return its path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4()}_{upload_file.filename}"
    file_path = UPLOAD_DIR / unique_filename

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await upload_file.read()
        await out_file.write(content)

    return file_path


async def cleanup_files(file_paths: List[Path]):
    """Clean up uploaded files after analysis."""
    for file_path in file_paths:
        try:
            if file_path.exists():
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")


@app.post(
    "/analyze/single",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_single_image(
    background_tasks: BackgroundTasks,
    task: str = Form(...),
    additional_patient_info: Optional[str] = Form(None),
    image: UploadFile = File(...),
):
    """
    Analyze a single MRI image.

    Parameters:
    - task: The analysis task or clinical question
    - additional_patient_info: Optional additional patient information
    - image: The MRI image file

    Returns:
    - Analysis results including findings and potential diagnoses
    """
    try:
        # Validate file type
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        file_path = await save_upload_file(image)
        background_tasks.add_task(cleanup_files, [file_path])

        # Run analysis
        result = mri_swarm(
            task=task,
            additional_patient_info=additional_patient_info,
            img=str(file_path),
            return_log=True,
        )

        return result

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/analyze/multiple",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_multiple_images(
    background_tasks: BackgroundTasks,
    task: str = Form(...),
    additional_patient_info: Optional[str] = Form(None),
    images: List[UploadFile] = File(...),
):
    """
    Analyze multiple MRI images.

    Parameters:
    - task: The analysis task or clinical question
    - additional_patient_info: Optional additional patient information
    - images: List of MRI image files

    Returns:
    - Analysis results including findings and potential diagnoses
    """
    try:
        # Validate number of images
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")

        # Validate file types and save files
        file_paths = []
        for image in images:
            if not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail=f"File {image.filename} must be an image"
                )
            file_path = await save_upload_file(image)
            file_paths.append(file_path)

        # Add cleanup task
        background_tasks.add_task(cleanup_files, file_paths)

        # Run analysis
        result = mri_swarm(
            task=task,
            additional_patient_info=additional_patient_info,
            imgs=[str(path) for path in file_paths],
            return_log=True,
        )

        return result

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/analyze/batch",
    response_model=List[dict],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_batch_images(
    background_tasks: BackgroundTasks,
    request: BatchMRIRequest,
    images: List[UploadFile] = File(...),
):
    """
    Analyze multiple MRI images in batch mode.

    Parameters:
    - tasks: List of analysis tasks or clinical questions for each case
    - patient_infos: List of patient information strings corresponding to each task
    - images: List of MRI image files corresponding to each task

    Returns:
    - List of analysis results, one for each case
    """
    try:
        # Validate input lengths match
        if not (len(request.tasks) == len(request.patient_infos) == len(images)):
            raise HTTPException(
                status_code=400,
                detail="Number of tasks, patient infos, and images must match",
            )

        # Validate file types and save files
        file_paths = []
        for image in images:
            if not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail=f"File {image.filename} must be an image"
                )
            file_path = await save_upload_file(image)
            file_paths.append(file_path)

        # Add cleanup task
        background_tasks.add_task(cleanup_files, file_paths)

        # Run batch analysis
        results = batched_mri_swarm(
            tasks=request.tasks,
            patient_infos=request.patient_infos,
            imgs=[str(path) for path in file_paths],
            return_log=True,
        )

        return results

    except ValueError as e:
        logger.error(f"Validation error in batch request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
