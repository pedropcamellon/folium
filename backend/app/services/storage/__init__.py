"""Cloud-agnostic object storage module

Supports multiple providers through abstract interface:
- AWS S3
- Azure Blob Storage
- RustFS (self-hosted S3-compatible)

Usage:
    from app.services.storage import get_storage

    storage = await get_storage()
    url = await storage.upload(key="file.pdf", data=bytes, content_type="application/pdf")
"""

from .aws_storage import AWSStorage
from .azure_storage import AzureStorage
from .base import ObjectStorageProvider, StorageConfig
from .factory import StorageProviderFactory, get_storage
from .s3_compatible_storage import S3CompatibleStorage

__all__ = [
    "AWSStorage",
    "AzureStorage",
    "ObjectStorageProvider",
    "S3CompatibleStorage",
    "StorageConfig",
    "StorageProviderFactory",
    "get_storage",
]
