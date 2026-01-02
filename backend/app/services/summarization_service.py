"""Summarization service client for calling summarization microservice"""

import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class SummarizationService:
    """Client for summarization microservice"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.SUMMARIZATION_SERVICE_URL
        self.timeout = 180.0  # 3 minutes for summarization (CPU-based LLM can be slow)

    async def summarize(
        self,
        transcript: str,
        format: str = "soap",
        interaction_type: Optional[str] = None,
        language: str = "en",
    ) -> dict:
        """
        Generate clinical summary from transcript.

        Args:
            transcript: Transcribed text to summarize
            format: "soap" for SOAP notes, "narrative" for free-text
            interaction_type: Type of interaction (optional)
            language: Language code (default: "en")

        Returns:
            {
                "summary": str,
                "structured_data": {
                    "chief_complaint": str,
                    "subjective": str,
                    "objective": str,
                    "assessment": str,
                    "plan": str,
                    "clinical_tags": list,
                    "icd_codes": list,
                    "action_items": list
                },
                "processing_time": float,
                "model_used": str,
                "provider": str
            }
        """
        logger.info(f"[REQUEST] Requesting summarization from {self.base_url}")
        logger.info(f"[INFO] Transcript length: {len(transcript)} chars, Format: {format}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "transcript": transcript,
                    "format": format,
                    "language": language,
                }
                if interaction_type:
                    payload["interaction_type"] = interaction_type

                logger.debug(f"[DEBUG] Payload: {payload}")

                response = await client.post(
                    f"{self.base_url}/summarize",
                    json=payload,
                )

                response.raise_for_status()
                result = response.json()

                logger.info(
                    f"[OK] Summarization complete ({result.get('processing_time', 0):.2f}s)"
                )
                logger.debug(f"[DEBUG] Summary length: {len(result.get('summary', ''))}")

                return result

            except httpx.TimeoutException:
                logger.error(f"[ERROR] Summarization timed out after {self.timeout}s")
                raise Exception(f"Summarization service timeout after {self.timeout}s")

            except httpx.HTTPStatusError as e:
                logger.error(f"[ERROR] Summarization failed: {e.response.status_code}")
                logger.error(f"[ERROR] Response: {e.response.text}")
                raise Exception(f"Summarization failed: {e.response.text}")

            except Exception as e:
                logger.error(f"[ERROR] Unexpected error calling summarization service: {e}")
                raise

    async def health_check(self) -> bool:
        """Check if summarization service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"[WARN] Summarization service health check failed: {e}")
            return False
