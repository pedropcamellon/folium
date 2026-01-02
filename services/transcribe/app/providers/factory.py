"""Provider factory for dependency injection"""

from typing import Optional
from .base import TranscriptionProvider
from .whisper import WhisperProvider
from .aws import AWSTranscribeProvider
from .azure import AzureSpeechProvider
from app.config import settings


# Provider registry
_provider_registry = {
    "whisper": WhisperProvider,
    "aws": AWSTranscribeProvider,
    "azure": AzureSpeechProvider,
}

# Singleton instance
_instance: Optional[TranscriptionProvider] = None


async def get_transcription_provider() -> TranscriptionProvider:
    """
    Get singleton transcription provider based on configuration.

    Provider is selected at startup via TRANSCRIPTION_PROVIDER env var.
    All requests use the same provider (no per-request provider selection).
    """
    global _instance

    if _instance is None:
        provider_class = _provider_registry.get(settings.TRANSCRIPTION_PROVIDER)

        if not provider_class:
            available = ", ".join(_provider_registry.keys())
            raise ValueError(
                f"Unknown provider: '{settings.TRANSCRIPTION_PROVIDER}'. "
                f"Available: {available}"
            )

        _instance = provider_class()
        await _instance.initialize()

    return _instance
