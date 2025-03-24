from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    content_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "success"

class FileUploadError(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FileMetadata(BaseModel):
    filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    s3_key: str
    bucket: str 