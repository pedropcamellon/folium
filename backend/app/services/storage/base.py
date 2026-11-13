"""Abstract base class for cloud-agnostic object storage"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StorageConfig:
    """Configuration for storage provider"""

    provider: str  # 'aws', 'azure', 'rustfs'
    bucket: str
    region: str
    endpoint_url: str | None = None
    public_endpoint_url: str | None = None  # For browser-accessible URLs
    access_key: str | None = None
    secret_key: str | None = None
    cdn_url: str | None = None
    # Provider-specific config
    connection_string: str | None = None  # Azure
    account_name: str | None = None  # Azure


class ObjectStorageProvider(ABC):
    """
    Abstract interface for object storage operations.
    Implementations: AWSStorage, AzureStorage, S3CompatibleStorage
    """

    def __init__(self, config: StorageConfig):
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize provider and ensure bucket/container exists"""

    @abstractmethod
    async def upload(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
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

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        Download file from storage

        Args:
            key: Storage path

        Returns:
            File bytes
        """

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete file from storage

        Args:
            key: Storage path

        Returns:
            True if successful
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if file exists

        Args:
            key: Storage path

        Returns:
            True if exists
        """

    @abstractmethod
    async def get_presigned_url(
        self, key: str, expiration: int = 3600, internal: bool = False
    ) -> str:
        """
        Generate temporary signed URL

        Args:
            key: Storage path
            expiration: URL expiration in seconds (default 1 hour)
            internal: If True, use internal endpoint for Docker service-to-service communication

        Returns:
            Presigned URL
        """

    @abstractmethod
    async def list_objects(self, prefix: str = "") -> list[str]:
        """
        List objects with optional prefix filter

        Args:
            prefix: Path prefix (e.g., "documents/")

        Returns:
            List of storage keys
        """
