import logging

import httpx

from app.contracts.voice_note_models import TranscriptionResult

logger = logging.getLogger(__name__)


class TranscriptionServiceClient:
    def __init__(self, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def transcribe(self, audio_url: str) -> TranscriptionResult:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/transcribe",
                json={
                    "audio_url": audio_url,
                    "language_code": "en-US",
                    "speaker_labels": False,
                },
            )
            response.raise_for_status()
            payload = response.json()

        logger.info("Transcription completed")
        return TranscriptionResult(
            transcript=payload.get("transcript", ""),
            language_code=payload.get("language_code"),
            confidence=payload.get("confidence"),
            processing_time=payload.get("processing_time"),
            provider=payload.get("provider"),
            raw=payload,
        )