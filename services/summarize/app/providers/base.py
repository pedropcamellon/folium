"""Base abstract class for summarization providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SummarizationProvider(ABC):
    """Abstract base class for LLM summarization providers.

    All providers (local, OpenAI, AWS Bedrock, Azure) must implement this interface.
    """

    @abstractmethod
    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured clinical summary from a transcript.

        Args:
            transcript: The clinical transcript text to summarize
            interaction_type: Type of interaction (e.g., "consultation", "follow-up")
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing:
                - summary: Full summary text
                - structured_data: Dict with clinical structure (SOAP format)
                - processing_time: Time taken in seconds
                - model_used: Name of the model used
                - usage: Optional token/cost information

        Raises:
            Exception: If summarization fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the name of the model being used.

        Returns:
            Model name string (e.g., "llama-3-8b-instruct", "gpt-4-turbo")
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the provider.

        Returns:
            Provider name string (e.g., "local", "openai", "bedrock", "azure")
        """
        pass
