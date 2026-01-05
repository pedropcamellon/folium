"""Abstract base class for cloud-agnostic object storage"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class StorageConfig:
    """Configuration for storage provider"""

    provider: str  # 'aws', 'azure', 'minio'
    bucket: str
    region: str
    endpoint_url: Optional[str] = None
    public_endpoint_url: Optional[str] = None  # For browser-accessible URLs
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    cdn_url: Optional[str] = None
    # Provider-specific config
    connection_string: Optional[str] = None  # Azure
    account_name: Optional[str] = None  # Azure


class ObjectStorageProvider(ABC):
    """
    Abstract interface for object storage operations.
    Implementations: AWSStorage, AzureStorage, MinIOStorage
    """

    def __init__(self, config: StorageConfig):
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize provider and ensure bucket/container exists"""
        pass

    @abstractmethod
    async def upload(
        self, key: str, data: bytes, content_type: str, metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file to storage

        Args:
            key: Storage path (e.g., "documents/file.pdf")
            data: File bytes
            content_type: MIME type
            metadata: Optional metadata tags

        Returns:
            Public URL or CDN URL
        """
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        Download file from storage

        Args:
            key: Storage path

        Returns:
            File bytes
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete file from storage

        Args:
            key: Storage path

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if file exists

        Args:
            key: Storage path

        Returns:
            True if exists
        """
        pass

    @abstractmethod
    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate temporary signed URL

        Args:
            key: Storage path
            expiration: URL validity in seconds

        Returns:
            Presigned URL
        """
        pass

    @abstractmethod
    async def list_objects(self, prefix: str = "") -> list[str]:
        """
        List objects with optional prefix filter

        Args:
            prefix: Path prefix (e.g., "documents/")

        Returns:
            List of storage keys
        """
        pass
