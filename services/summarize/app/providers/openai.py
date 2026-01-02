"""OpenAI provider for summarization (planned implementation)."""

import logging
from typing import Dict, Any, Optional

from app.providers.base import SummarizationProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(SummarizationProvider):
    """OpenAI GPT provider for clinical summarization.

    Status: Planned implementation (Phase 2)
    Requirements: OpenAI API key, Business Associate Agreement (BAA) for HIPAA
    """

    def __init__(self):
        logger.info("🔵 OpenAI provider initialized (not yet implemented)")
        raise NotImplementedError(
            "OpenAI provider not yet implemented. "
            "Use SUMMARIZATION_PROVIDER=local for MVP."
        )

    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError("OpenAI provider not implemented")

    def get_model_name(self) -> str:
        return "gpt-4-turbo"

    def get_provider_name(self) -> str:
        return "openai"
