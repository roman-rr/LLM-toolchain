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

@router.post("/upload/s3",
    response_model=List[FileUploadResponse],
    summary="Upload multiple files (max 3 files, 10MB each)",
    description="Upload multiple files (PDF, DOC, TXT) in a single request"
)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 files can be uploaded at once")

    responses = []
    errors = []
    
    for file in files:
        try:
            # Debug logging
            logger.info(f"Processing file: {file.filename}, size: {file.size}, type: {file.content_type}")
            
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
            else:
                errors.append(f"Failed to get URL for {file.filename}")
        except HTTPException as he:
            logger.error(f"Validation error for {file.filename}: {str(he.detail)}")
            raise he
        except Exception as e:
            error_msg = f"Error uploading {file.filename}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

    if not responses and errors:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "All file uploads failed",
                "errors": errors
            }
        )

    return responses