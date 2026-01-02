"""Configuration settings for transcription service"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment configuration with provider selection"""
    
    # Provider selection (ONE active at a time)
    TRANSCRIPTION_PROVIDER: str = "whisper"  # "whisper" | "aws" | "azure"
    
    # Self-hosted Whisper settings
    WHISPER_MODEL_SIZE: str = "base"  # tiny|base|small|medium|large
    WHISPER_DEVICE: str = "cpu"       # cpu|cuda
    
    # AWS Transcribe settings (if TRANSCRIPTION_PROVIDER=aws)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    TEMP_S3_BUCKET: str = ""
    
    # Azure Speech settings (if TRANSCRIPTION_PROVIDER=azure)
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"
    
    # Service settings
    PORT: int = 8001
    LOG_LEVEL: str = "info"
    MAX_AUDIO_SIZE_MB: int = 100
    TRANSCRIBE_TIMEOUT_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
