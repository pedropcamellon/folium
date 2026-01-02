"""Provider factory for summarization service.

Public API: get_summarization_provider()
"""

import logging
from functools import lru_cache

from app.providers.base import SummarizationProvider
from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_summarization_provider() -> SummarizationProvider:
    """Get the configured summarization provider (singleton).

    Provider is cached after first call to avoid reloading models.
    Selection based on SUMMARIZATION_PROVIDER environment variable.

    Returns:
        SummarizationProvider instance (local, openai, bedrock, or azure)

    Raises:
        ValueError: If provider not recognized
        NotImplementedError: If provider not yet implemented
    """
    provider_name = settings.summarization_provider.lower()

    logger.info(f"[INIT] Initializing summarization provider: {provider_name}")

    if provider_name == "local":
        from app.providers.local import LocalLLMProvider

        return LocalLLMProvider()

    elif provider_name == "openai":
        from app.providers.openai import OpenAIProvider

        return OpenAIProvider()

    elif provider_name == "bedrock":
        from app.providers.bedrock import BedrockProvider

        return BedrockProvider()

    elif provider_name == "azure":
        from app.providers.azure import AzureOpenAIProvider

        return AzureOpenAIProvider()

    else:
        raise ValueError(
            f"Unknown summarization provider: {provider_name}. "
            f"Valid options: local, openai, bedrock, azure"
        )


__all__ = ["get_summarization_provider", "SummarizationProvider"]
