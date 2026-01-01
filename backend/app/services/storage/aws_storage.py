"""AWS S3 storage provider implementation"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
from typing import Optional

from .base import ObjectStorageProvider, StorageConfig

logger = logging.getLogger(__name__)


class AWSStorage(ObjectStorageProvider):
    """AWS S3 storage implementation"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._client = None
    
    async def initialize(self) -> None:
        """Initialize S3 client and ensure bucket exists"""
        self._client = boto3.client(
            's3',
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
            region_name=self.config.region,
            config=Config(signature_version='s3v4')
        )
        
        # Check bucket exists
        try:
            self._client.head_bucket(Bucket=self.config.bucket)
            logger.info(f"AWS S3: Connected to bucket '{self.config.bucket}'")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Create bucket if doesn't exist
                self._client.create_bucket(
                    Bucket=self.config.bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.config.region}
                )
                logger.info(f"AWS S3: Created bucket '{self.config.bucket}'")
            else:
                raise
    
    async def upload(
        self, 
        key: str, 
        data: bytes, 
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload to S3"""
        extra_args = {
            'ContentType': content_type
        }
        if metadata:
            extra_args['Metadata'] = metadata
        
        self._client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=data,
            **extra_args
        )
        
        logger.info(f"AWS S3: Uploaded {key}")
        
        # Return CDN URL or S3 URL
        if self.config.cdn_url:
            return f"{self.config.cdn_url}/{key}"
        return f"https://{self.config.bucket}.s3.{self.config.region}.amazonaws.com/{key}"
    
    async def download(self, key: str) -> bytes:
        """Download from S3"""
        response = self._client.get_object(Bucket=self.config.bucket, Key=key)
        data = response['Body'].read()
        logger.info(f"AWS S3: Downloaded {key}")
        return data
    
    async def delete(self, key: str) -> bool:
        """Delete from S3"""
        try:
            self._client.delete_object(Bucket=self.config.bucket, Key=key)
            logger.info(f"AWS S3: Deleted {key}")
            return True
        except ClientError as e:
            logger.error(f"AWS S3: Delete failed for {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if object exists in S3"""
        try:
            self._client.head_object(Bucket=self.config.bucket, Key=key)
            return True
        except ClientError:
            return False
    
    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL"""
        url = self._client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.config.bucket, 'Key': key},
            ExpiresIn=expiration
        )
        logger.info(f"AWS S3: Generated presigned URL for {key}")
        return url
    
    async def list_objects(self, prefix: str = "") -> list[str]:
        """List objects with prefix"""
        paginator = self._client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.config.bucket, Prefix=prefix)
        
        keys = []
        for page in pages:
            for obj in page.get('Contents', []):
                keys.append(obj['Key'])
        
        return keys
