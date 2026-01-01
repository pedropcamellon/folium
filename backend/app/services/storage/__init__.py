"""Cloud-agnostic object storage module

Supports multiple providers through abstract interface:
- AWS S3
- Azure Blob Storage
- MinIO (self-hosted)

Usage:
    from app.services.storage import get_storage
    
    storage = await get_storage()
    url = await storage.upload(key="file.pdf", data=bytes, content_type="application/pdf")
"""

from .base import ObjectStorageProvider, StorageConfig
from .factory import get_storage, StorageProviderFactory
from .aws_storage import AWSStorage
from .azure_storage import AzureStorage
from .minio_storage import MinIOStorage

__all__ = [
    'ObjectStorageProvider',
    'StorageConfig',
    'get_storage',
    'StorageProviderFactory',
    'AWSStorage',
    'AzureStorage',
    'MinIOStorage'
]
