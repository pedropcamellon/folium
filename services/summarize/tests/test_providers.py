"""Test summarization providers."""

import pytest
from app.providers.base import SummarizationProvider


class TestProviderInterface:
    """Test that all providers implement the required interface."""

    @pytest.mark.asyncio
    async def test_local_provider_interface(self):
        """Test that LocalLLMProvider implements SummarizationProvider."""
        from app.providers.local import LocalLLMProvider

        assert issubclass(LocalLLMProvider, SummarizationProvider)

        # Check methods exist
        provider = LocalLLMProvider()
        assert hasattr(provider, "summarize")
        assert hasattr(provider, "get_model_name")
        assert hasattr(provider, "get_provider_name")

        assert provider.get_provider_name() == "local"

    def test_openai_provider_not_implemented(self):
        """Test that OpenAI provider raises NotImplementedError."""
        from app.providers.openai import OpenAIProvider

        with pytest.raises(NotImplementedError):
            OpenAIProvider()

    def test_bedrock_provider_not_implemented(self):
        """Test that Bedrock provider raises NotImplementedError."""
        from app.providers.bedrock import BedrockProvider

        with pytest.raises(NotImplementedError):
            BedrockProvider()

    def test_azure_provider_not_implemented(self):
        """Test that Azure provider raises NotImplementedError."""
        from app.providers.azure import AzureOpenAIProvider

        with pytest.raises(NotImplementedError):
            AzureOpenAIProvider()


class TestProviderFactory:
    """Test provider factory."""

    def test_factory_local_provider(self, monkeypatch):
        """Test factory returns local provider."""
        from app.providers import get_summarization_provider
        from app.providers.local import LocalLLMProvider

        # Clear cache
        get_summarization_provider.cache_clear()

        monkeypatch.setenv("SUMMARIZATION_PROVIDER", "local")

        provider = get_summarization_provider()
        assert isinstance(provider, LocalLLMProvider)

    def test_factory_invalid_provider(self, monkeypatch):
        """Test factory raises ValueError for invalid provider."""
        from app.providers import get_summarization_provider

        # Clear cache
        get_summarization_provider.cache_clear()

        monkeypatch.setenv("SUMMARIZATION_PROVIDER", "invalid")

        with pytest.raises(ValueError, match="Unknown summarization provider"):
            get_summarization_provider()
