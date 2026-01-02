"""AWS Bedrock provider for summarization (planned implementation)."""

import logging
from typing import Dict, Any, Optional

from app.providers.base import SummarizationProvider

logger = logging.getLogger(__name__)


class BedrockProvider(SummarizationProvider):
    """AWS Bedrock provider for clinical summarization.

    Status: Planned implementation (Phase 2)
    Requirements: AWS credentials, Business Associate Agreement (BAA) for HIPAA
    Models: Claude 3 (Sonnet/Haiku), Llama 3, Titan
    """

    def __init__(self):
        logger.info("🟠 AWS Bedrock provider initialized (not yet implemented)")
        raise NotImplementedError(
            "AWS Bedrock provider not yet implemented. "
            "Use SUMMARIZATION_PROVIDER=local for MVP."
        )

    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError("Bedrock provider not implemented")

    def get_model_name(self) -> str:
        return "anthropic.claude-3-sonnet"

    def get_provider_name(self) -> str:
        return "bedrock"
