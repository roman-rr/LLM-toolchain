from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from api.services.s3 import S3Service
from api.schemas.file import FileUploadResponse, FileUploadError, FileMetadata
from api.utils.logger import logger
from typing import List, Optional
import time
from datetime import datetime

router = APIRouter()
s3_service = S3Service()

@router.get("/",
    response_model=dict,
    summary="API Root Endpoint",
    description="Returns API status and version information",
    tags=["System"]
)
async def get_root():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "File Upload API is running"
    }

@router.post("/upload/batch",
    response_model=List[FileUploadResponse],
    summary="Upload multiple files",
    description="Upload multiple files in a single request"
)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    responses = []
    for file in files:
        try:
            file_url = await s3_service.upload_file(file)
            if file_url:
                responses.append(
                    FileUploadResponse(
                        filename=file.filename,
                        file_url=file_url,
                        file_size=file.size,
                        content_type=file.content_type
                    )
                )
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {str(e)}")
            continue
    return responses