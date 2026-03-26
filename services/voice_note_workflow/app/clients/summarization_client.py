import logging

import httpx

from app.contracts.voice_note_models import SummaryResult

logger = logging.getLogger(__name__)


class SummarizationServiceClient:
    def __init__(self, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def summarize(self, transcript: str) -> SummaryResult:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/summarize",
                json={
                    "transcript": transcript,
                    "format": "soap",
                    "language": "en",
                },
            )
            response.raise_for_status()
            payload = response.json()

        logger.info("Summarization completed")
        return SummaryResult(
            summary=payload.get("summary", ""),
            structured_summary=payload.get("structured_data"),
            processing_time=payload.get("processing_time"),
            provider=payload.get("provider"),
            model_used=payload.get("model_used"),
            raw=payload,
        )