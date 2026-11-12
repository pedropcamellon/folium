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

    @pytest.mark.asyncio
    async def test_local_provider_forwards_sampling_parameters(self, monkeypatch):
        """Test that local provider sampling parameters reach the inference engine."""
        from app.providers.local import LocalLLMProvider
        from app.providers import local as local_provider_module

        captured_arguments = {}

        class FakeModel:
            def create_chat_completion(self, **kwargs):
                captured_arguments.update(kwargs)
                return {
                    "choices": [{"message": {"content": "A concise summary."}}],
                    "usage": {},
                }

        monkeypatch.setattr(
            local_provider_module.local_inference_engine,
            "_get_model",
            lambda: FakeModel(),
        )

        def fake_format_prompt(transcript, format):
            return transcript

        monkeypatch.setattr(
            local_provider_module,
            "format_prompt",
            fake_format_prompt,
        )

        result = await LocalLLMProvider().summarize(
            "Synthetic follow-up transcript.", format="narrative"
        )

        assert result["summary"] == "A concise summary."
        assert captured_arguments["top_p"] == 0.9
        assert captured_arguments["repeat_penalty"] == 1.1

    def test_local_inference_forwards_sampling_parameters(self, monkeypatch):
        """Test local inference forwards sampling parameters to llama.cpp."""
        from app.inference.local import LocalInferenceEngine

        captured_arguments = {}

        class FakeModel:
            def create_chat_completion(self, **kwargs):
                captured_arguments.update(kwargs)
                return {"choices": []}

        engine = LocalInferenceEngine()
        monkeypatch.setattr(engine, "_get_model", lambda: FakeModel())
        engine.chat_completion(
            messages=[{"role": "user", "content": "Synthetic input"}],
            top_p=0.65,
            repeat_penalty=1.3,
        )

        assert captured_arguments["top_p"] == 0.65
        assert captured_arguments["repeat_penalty"] == 1.3

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
