from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TEMPORAL_ADDRESS: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"
    VOICE_NOTE_TASK_QUEUE: str = "voice-notes-queue"

    BACKEND_API_URL: str = "http://localhost:8000"
    BACKEND_API_TOKEN: str | None = None

    TRANSCRIPTION_SERVICE_URL: str = "http://localhost:8001"
    SUMMARIZATION_SERVICE_URL: str = "http://localhost:8002"

    REQUEST_TIMEOUT_SECONDS: float = 30.0
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()