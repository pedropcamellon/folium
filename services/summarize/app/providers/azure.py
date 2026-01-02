"""Azure OpenAI provider for summarization (planned implementation)."""

import logging
from typing import Dict, Any, Optional

from app.providers.base import SummarizationProvider

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(SummarizationProvider):
    """Azure OpenAI provider for clinical summarization.

    Status: Planned implementation (Phase 2)
    Requirements: Azure OpenAI resource, Business Associate Agreement (BAA) for HIPAA
    Models: GPT-4, GPT-3.5 (Azure-hosted)
    """

    def __init__(self):
        logger.info("🔷 Azure OpenAI provider initialized (not yet implemented)")
        raise NotImplementedError(
            "Azure OpenAI provider not yet implemented. "
            "Use SUMMARIZATION_PROVIDER=local for MVP."
        )

    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError("Azure OpenAI provider not implemented")

    def get_model_name(self) -> str:
        return "gpt-4"

    def get_provider_name(self) -> str:
        return "azure"
