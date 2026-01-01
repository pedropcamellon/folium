"""Unified storage service for multi-cloud object storage (AWS S3, Azure Blob, MinIO)"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class UnifiedStorageService:
    """
    Cloud-agnostic object storage abstraction using S3-compatible API.
    Supports multiple backends without vendor lock-in:
    - AWS S3 (production)
    - Azure Blob Storage (via S3 compatibility layer)
    - MinIO (local development, on-premise)
    """
    
    def __init__(self):
        """Initialize object storage client with environment-specific configuration"""
        # boto3 provides S3-compatible API that works with all backends
        self._client = boto3.client(
            's3',
            endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.STORAGE_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist (useful for MinIO dev environment)"""
        try:
            self._client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except ClientError:
            try:
                self._client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            except ClientError as e:
                logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str) -> str:
        """
        Upload file to object storage
        
        Args:
            file_data: Raw file bytes
            key: Storage path/key (e.g., "documents/abc-123/file.pdf")
            content_type: MIME type (e.g., "application/pdf")
        
        Returns:
            Public URL or CDN URL if configured
        """
        try:
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type
            )
            logger.info(f"Uploaded file: {key}")
            
            # Return CDN URL if configured, otherwise storage endpoint URL
            if settings.STORAGE_CDN_URL:
                return f"{settings.STORAGE_CDN_URL}/{key}"
            else:
                return f"{settings.STORAGE_ENDPOINT}/{self.bucket_name}/{key}"
        
        except ClientError as e:
            logger.error(f"Failed to upload {key}: {e}")
            raise
    
    async def download_file(self, key: str) -> bytes:
        """
        Download file from object storage
        
        Args:
            key: Storage path/key
        
        Returns:
            Raw file bytes
        """
        try:
            response = self._client.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read()
            logger.info(f"Downloaded file: {key}")
            return data
        except ClientError as e:
            logger.error(f"Failed to download {key}: {e}")
            raise
    
    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for temporary access
        
        Args:
            key: Storage path/key
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            Presigned URL
        """
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for {key} (expires in {expiration}s)")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {key}: {e}")
            raise
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete file from storage
        
        Args:
            key: Storage path/key
        
        Returns:
            True if successful
        """
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted file: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False
    
    async def file_exists(self, key: str) -> bool:
        """
        Check if file exists in storage
        
        Args:
            key: Storage path/key
        
        Returns:
            True if file exists
        """
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False


# Singleton instance
_storage_service: Optional[UnifiedStorageService] = None


def get_storage_service() -> UnifiedStorageService:
    """Get or create singleton storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = UnifiedStorageService()
    return _storage_service
