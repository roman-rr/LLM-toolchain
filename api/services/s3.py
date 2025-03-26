import boto3

from config.settings import settings
from api.utils.logger import logger
from fastapi import UploadFile, HTTPException
from typing import Optional


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def upload_file(self, file: UploadFile) -> Optional[str]:
        # Validate file type
        allowed_types = ['application/pdf', 'text/plain', 'application/msword',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not allowed. Only PDF, TXT, and DOC files are supported.")

        # Validate file size (10MB = 10 * 1024 * 1024 bytes)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

        try:
            # Debug logging
            logger.info(f"Attempting to upload {file.filename} to S3")
            
            file_key = f"uploads/{file.filename}"
            
            # Make sure file is at start position
            await file.seek(0)
            
            # Read file content
            content = await file.read()
            
            # Use regular boto3 upload without await
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=content
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            logger.info(f"Successfully uploaded to {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise Exception(f"S3 upload failed: {str(e)}") 