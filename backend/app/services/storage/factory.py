"""Factory for creating storage provider instances"""

import logging
from typing import Optional

from .base import ObjectStorageProvider, StorageConfig
from .aws_storage import AWSStorage
from .azure_storage import AzureStorage
from .minio_storage import MinIOStorage

logger = logging.getLogger(__name__)


class StorageProviderFactory:
    """Factory for instantiating storage providers"""

    _providers = {"aws": AWSStorage, "azure": AzureStorage, "minio": MinIOStorage}

    @classmethod
    def create(cls, config: StorageConfig) -> ObjectStorageProvider:
        """
        Create storage provider instance based on configuration

        Args:
            config: Storage configuration with provider type

        Returns:
            Initialized storage provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        provider_class = cls._providers.get(config.provider.lower())

        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported storage provider: '{config.provider}'. "
                f"Supported providers: {supported}"
            )

        logger.info(f"Creating storage provider: {config.provider}")
        return provider_class(config)

    @classmethod
    def register_provider(cls, name: str, provider_class: type[ObjectStorageProvider]):
        """
        Register custom storage provider

        Args:
            name: Provider identifier (e.g., 'gcs', 'r2')
            provider_class: Provider implementation class
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered custom storage provider: {name}")


# Singleton instance
_storage_instance: Optional[ObjectStorageProvider] = None


async def get_storage() -> ObjectStorageProvider:
    """
    Get or create singleton storage provider instance

    Returns:
        Initialized storage provider
    """
    global _storage_instance

    if _storage_instance is None:
        from app.config import settings

        # Build config from settings
        config = StorageConfig(
            provider=settings.STORAGE_PROVIDER,
            bucket=settings.STORAGE_BUCKET,
            region=settings.STORAGE_REGION,
            endpoint_url=settings.STORAGE_ENDPOINT,
            public_endpoint_url=settings.STORAGE_PUBLIC_ENDPOINT,
            access_key=settings.STORAGE_ACCESS_KEY,
            secret_key=settings.STORAGE_SECRET_KEY,
            cdn_url=settings.STORAGE_CDN_URL,
            connection_string=settings.AZURE_STORAGE_CONNECTION_STRING,
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
        )

        # Create and initialize provider
        _storage_instance = StorageProviderFactory.create(config)
        await _storage_instance.initialize()

    return _storage_instance
