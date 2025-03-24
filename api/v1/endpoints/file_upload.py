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

@router.post("/upload", 
    response_model=FileUploadResponse,
    responses={400: {"model": FileUploadError}},
    summary="Upload a single file",
    description="Upload a file (PDF, TXT, DOC) to S3 bucket"
)
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Query(None, description="Optional folder path in S3")
):
    try:
        if not file.content_type in ["application/pdf", "text/plain", "application/msword"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        start_time = time.time()
        file_url = await s3_service.upload_file(file, folder)
        
        if not file_url:
            raise HTTPException(status_code=400, detail="Failed to upload file")
        
        return FileUploadResponse(
            filename=file.filename,
            file_url=file_url,
            file_size=file.size,
            content_type=file.content_type,
            upload_timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

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

@router.get("/files",
    response_model=List[FileMetadata],
    summary="List uploaded files",
    description="Get a list of all uploaded files"
)
async def list_files(
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    limit: int = Query(100, description="Maximum number of files to return")
):
    try:
        files = await s3_service.list_files(file_type, limit)
        return files
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list files")

@router.delete("/files/{file_id}",
    response_model=dict,
    summary="Delete a file",
    description="Delete a file from S3 bucket"
)
async def delete_file(file_id: str):
    try:
        await s3_service.delete_file(file_id)
        return {"status": "success", "message": f"File {file_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 