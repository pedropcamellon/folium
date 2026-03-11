"""Azure Blob Storage provider implementation"""

from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
import logging
from typing import Optional

from .base import ObjectStorageProvider, StorageConfig

logger = logging.getLogger(__name__)


class AzureStorage(ObjectStorageProvider):
    """Azure Blob Storage implementation"""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._service_client: Optional[BlobServiceClient] = None
        self._container_client: Optional[ContainerClient] = None

    async def initialize(self) -> None:
        """Initialize Azure Blob Storage client and ensure container exists"""
        # Initialize service client
        if self.config.connection_string:
            self._service_client = BlobServiceClient.from_connection_string(
                self.config.connection_string
            )
        else:
            # Use account name + key
            account_url = f"https://{self.config.account_name}.blob.core.windows.net"
            self._service_client = BlobServiceClient(
                account_url=account_url, credential=self.config.secret_key
            )

        # Get container client
        self._container_client = self._service_client.get_container_client(self.config.bucket)

        # Create container if doesn't exist
        try:
            await self._container_client.create_container()
            logger.info(f"Azure Blob: Created container '{self.config.bucket}'")
        except ResourceExistsError:
            logger.info(f"Azure Blob: Connected to container '{self.config.bucket}'")

    async def upload(
        self, key: str, data: bytes, content_type: str, metadata: Optional[dict] = None
    ) -> str:
        """Upload to Azure Blob"""
        blob_client = self._container_client.get_blob_client(key)

        await blob_client.upload_blob(
            data, overwrite=True, content_settings={"content_type": content_type}, metadata=metadata
        )

        logger.info(f"Azure Blob: Uploaded {key}")

        # Return CDN URL or blob URL
        if self.config.cdn_url:
            return f"{self.config.cdn_url}/{key}"
        return blob_client.url

    async def download(self, key: str) -> bytes:
        """Download from Azure Blob"""
        blob_client = self._container_client.get_blob_client(key)
        stream = await blob_client.download_blob()
        data = await stream.readall()
        logger.info(f"Azure Blob: Downloaded {key}")
        return data

    async def delete(self, key: str) -> bool:
        """Delete from Azure Blob"""
        try:
            blob_client = self._container_client.get_blob_client(key)
            await blob_client.delete_blob()
            logger.info(f"Azure Blob: Deleted {key}")
            return True
        except Exception as e:
            logger.error(f"Azure Blob: Delete failed for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if blob exists"""
        try:
            blob_client = self._container_client.get_blob_client(key)
            await blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False

    async def get_presigned_url(
        self, key: str, expiration: int = 3600, internal: bool = False
    ) -> str:
        """Generate SAS URL (Azure's presigned URL)"""
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta

        blob_client = self._container_client.get_blob_client(key)

        sas_token = generate_blob_sas(
            account_name=self.config.account_name,
            container_name=self.config.bucket,
            blob_name=key,
            account_key=self.config.secret_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expiration),
        )

        url = f"{blob_client.url}?{sas_token}"
        logger.info(f"Azure Blob: Generated SAS URL for {key}")
        return url

    async def list_objects(self, prefix: str = "") -> list[str]:
        """List blobs with prefix"""
        keys = []
        async for blob in self._container_client.list_blobs(name_starts_with=prefix):
            keys.append(blob.name)
        return keys

    async def close(self):
        """Close Azure clients"""
        if self._service_client:
            await self._service_client.close()
