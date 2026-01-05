"""MinIO storage provider implementation"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
from typing import Optional

from .base import ObjectStorageProvider, StorageConfig

logger = logging.getLogger(__name__)


class MinIOStorage(ObjectStorageProvider):
    """MinIO storage implementation (uses S3-compatible API)"""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._client = None

    async def initialize(self) -> None:
        """Initialize MinIO client and ensure bucket exists"""
        self._client = boto3.client(
            "s3",
            endpoint_url=self.config.endpoint_url,
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
            region_name=self.config.region,
            config=Config(signature_version="s3v4"),
        )

        # Check bucket exists, create if not
        try:
            self._client.head_bucket(Bucket=self.config.bucket)
            logger.info(f"MinIO: Connected to bucket '{self.config.bucket}'")
        except ClientError:
            self._client.create_bucket(Bucket=self.config.bucket)
            logger.info(f"MinIO: Created bucket '{self.config.bucket}'")

    async def upload(
        self, key: str, data: bytes, content_type: str, metadata: Optional[dict] = None
    ) -> str:
        """Upload to MinIO"""
        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        self._client.put_object(Bucket=self.config.bucket, Key=key, Body=data, **extra_args)

        logger.info(f"MinIO: Uploaded {key}")

        # Return URL
        if self.config.cdn_url:
            return f"{self.config.cdn_url}/{key}"
        return f"{self.config.endpoint_url}/{self.config.bucket}/{key}"

    async def download(self, key: str) -> bytes:
        """Download from MinIO"""
        response = self._client.get_object(Bucket=self.config.bucket, Key=key)
        data = response["Body"].read()
        logger.info(f"MinIO: Downloaded {key}")
        return data

    async def delete(self, key: str) -> bool:
        """Delete from MinIO"""
        try:
            self._client.delete_object(Bucket=self.config.bucket, Key=key)
            logger.info(f"MinIO: Deleted {key}")
            return True
        except ClientError as e:
            logger.error(f"MinIO: Delete failed for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if object exists in MinIO"""
        try:
            self._client.head_object(Bucket=self.config.bucket, Key=key)
            return True
        except ClientError:
            return False

    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL with public endpoint for browser access"""
        logger.info(f"MinIO: Generating presigned URL for key={key}")
        logger.info(f"MinIO: Config - endpoint_url={self.config.endpoint_url}")
        logger.info(f"MinIO: Config - public_endpoint_url={self.config.public_endpoint_url}")

        # If we have a public endpoint, create a temporary client with that endpoint
        # to generate the signature correctly
        if self.config.public_endpoint_url:
            logger.info("MinIO: Using public endpoint for presigned URL generation")
            public_client = boto3.client(
                "s3",
                endpoint_url=self.config.public_endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region,
                config=Config(signature_version="s3v4"),
            )
            url = public_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.config.bucket, "Key": key},
                ExpiresIn=expiration,
            )
        else:
            # Fallback to internal endpoint
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.config.bucket, "Key": key},
                ExpiresIn=expiration,
            )

        logger.info(f"MinIO: Generated presigned URL: {url}")
        return url

    async def list_objects(self, prefix: str = "") -> list[str]:
        """List objects with prefix"""
        try:
            response = self._client.list_objects_v2(Bucket=self.config.bucket, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError:
            return []
