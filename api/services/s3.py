import boto3
from config.settings import settings
from api.utils.logger import logger
from fastapi import UploadFile
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
        try:
            file_key = f"uploads/{file.filename}"
            await self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_key
            )
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return None 