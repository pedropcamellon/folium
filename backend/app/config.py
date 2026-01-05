"""Application configuration using Pydantic settings"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App settings
    APP_NAME: str = "SouthDrift"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://frontend:3000",
        "http://127.0.0.1:3000",
    ]

    # Database (future)
    DATABASE_URL: str = "sqlite:///./southdrift.db"

    # Multi-Cloud Storage Configuration
    STORAGE_PROVIDER: str = "minio"  # 'aws', 'azure', 'minio'
    STORAGE_BUCKET: str = "southdrift-dev"
    STORAGE_REGION: str = "us-east-2"
    STORAGE_ENDPOINT: str | None = None  # Required for MinIO/Azure (internal Docker)
    STORAGE_PUBLIC_ENDPOINT: str | None = None  # Public-facing endpoint for browser
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_CDN_URL: str | None = None  # Optional CDN URL

    # Azure-specific storage settings
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_ACCOUNT_NAME: str = ""

    # Transcription Service
    TRANSCRIPTION_SERVICE_URL: str = (
        "http://localhost:8001"  # or "http://transcribe:8001" in docker-compose
    )

    # Summarization Service
    SUMMARIZATION_SERVICE_URL: str = (
        "http://localhost:8002"  # or "http://summarize:8002" in docker-compose
    )

    # Legacy settings (deprecated)

    # AWS
    AWS_LAMBDA_ENDPOINT: str = ""
    AWS_REGION: str = "us-east-1"

    # Azure AI
    AZURE_FUNCTIONS_ENDPOINT: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables (e.g., from .NET Core)


settings = Settings()
