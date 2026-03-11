"""Transcription service client for calling transcription microservice"""

import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Client for transcription microservice"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.TRANSCRIPTION_SERVICE_URL
        self.timeout = 300.0  # 5 minutes for transcription

    async def transcribe(
        self,
        audio_url: str,
        language_code: str = "en-US",
        speaker_labels: bool = False,
        vocabulary_name: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio file from presigned URL.

        Args:
            audio_url: Presigned URL to audio file (any storage provider)
            language_code: Language code (e.g., "en-US")
            speaker_labels: Enable speaker diarization
            vocabulary_name: Custom medical vocabulary (AWS/Azure only)

        Returns:
            {
                "transcript": str,
                "language_code": str,
                "confidence": float | None,
                "segments": [...],
                "processing_time": float
            }
        """

        logger.info(f"Requesting transcription from {self.base_url}")
        logger.info(f"Audio URL: {audio_url[:80]}...")
        logger.info(f"Language: {language_code}, Speaker labels: {speaker_labels}")

        if language_code is None:
            logger.warning("Language was provided as None. Using auto instead...")
            language_code = "auto"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "audio_url": audio_url,
                    "language_code": language_code,
                    "speaker_labels": speaker_labels,
                    "vocabulary_name": vocabulary_name,
                }
                logger.info(f"Sending POST to {self.base_url}/transcribe")

                response = await client.post(
                    f"{self.base_url}/transcribe",
                    json=payload,
                )

                logger.info(f"Response status: {response.status_code}")
                response.raise_for_status()

                result = response.json()
                logger.info(f"Transcription completed in {result.get('processing_time', 0):.2f}s")
                logger.info(f"Transcript preview: {result.get('transcript', '')[:100]}...")
                logger.info(f"Full result keys: {result.keys()}")

                return result

            except httpx.HTTPStatusError as e:
                logger.error(f"Transcription HTTP error: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
                raise RuntimeError(f"Transcription service error: {e.response.status_code}")

            except httpx.TimeoutException:
                logger.error(f"Transcription timeout after {self.timeout}s")
                raise RuntimeError("Transcription service timeout")

            except Exception as e:
                logger.error(f"Transcription error: {type(e).__name__}: {e}", exc_info=True)
                raise

    async def health_check(self) -> dict:
        """Check if transcription service is healthy"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Transcription service health check failed: {e}")
                return {"status": "unhealthy", "error": str(e)}


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get singleton transcription service instance"""
    global _transcription_service

    if _transcription_service is None:
        _transcription_service = TranscriptionService()

    return _transcription_service
