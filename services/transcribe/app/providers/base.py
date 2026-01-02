"""Abstract base class for transcription providers"""

from abc import ABC, abstractmethod
from typing import Optional


class TranscriptionProvider(ABC):
    """Abstract base class for transcription providers"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize provider (load models, setup clients, etc.)"""
        pass

    @abstractmethod
    async def transcribe(
        self,
        audio_url: str,
        language_code: str = "en-US",
        speaker_labels: bool = False,
        vocabulary_name: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio from URL.

        Args:
            audio_url: Presigned URL to audio file
            language_code: Language code (e.g., "en-US")
            speaker_labels: Enable speaker diarization
            vocabulary_name: Custom vocabulary name (AWS/Azure)

        Returns:
            {
                "transcript": str,
                "language_code": str,
                "confidence": float | None,
                "segments": [{"start_time": float, "end_time": float, "text": str}],
                "processing_time": float,
                "job_id": str | None
            }
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for health checks"""
        pass
