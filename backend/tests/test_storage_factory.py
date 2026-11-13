from app.services.storage.factory import StorageProviderFactory
from app.services.storage.s3_compatible_storage import S3CompatibleStorage
from app.services.storage.base import StorageConfig


def test_rustfs_provider_uses_s3_compatible_storage() -> None:
    config = StorageConfig(provider="rustfs", bucket="test-bucket", region="us-east-1")

    provider = StorageProviderFactory.create(config)

    assert isinstance(provider, S3CompatibleStorage)
