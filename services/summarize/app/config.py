"""Configuration settings for summarization service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Service Configuration
    service_name: str = "summarize"
    service_port: int = 8002

    # Provider Selection
    summarization_provider: str = "local"  # local, openai, bedrock, azure

    # Local LLM Settings
    local_model_path: Optional[str] = None  # Path to GGUF model file
    local_model_name: str = "mediphi-clinical"  # Model name for logging
    local_n_ctx: int = 8192  # Context window
    local_n_threads: Optional[int] = 4  # CPU threads
    local_temperature: float = 0.0  # Greedy decoding = fastest
    local_max_tokens: int = 800  # Token limit for summary

    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo"  # or gpt-3.5-turbo
    openai_temperature: float = 0.3
    openai_max_tokens: int = 500

    # AWS Bedrock Settings
    aws_region: Optional[str] = "us-east-1"
    aws_bedrock_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    aws_bedrock_temperature: float = 0.3
    aws_bedrock_max_tokens: int = 500

    # Azure OpenAI Settings
    azure_openai_endpoint: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_deployment: str = "gpt-4.1-nano"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_temperature: float = 1.0  # reasoning models only support 1.0
    azure_openai_max_tokens: int = 2000  # Reasoning models need headroom

    # CORS Settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://frontend:3000",
    ]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
