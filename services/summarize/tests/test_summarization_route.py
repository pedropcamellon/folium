"""HTTP-level regression coverage for local summarization."""

from fastapi.testclient import TestClient

from app.config import settings
from app.inference.local import local_inference_engine
from app.main import app
from app.providers import get_summarization_provider
from app.providers import local as local_provider_module


def test_summarize_endpoint_uses_configured_local_provider(monkeypatch, request):
    captured_arguments = {}

    class FakeModel:
        def create_chat_completion(self, **kwargs):
            captured_arguments.update(kwargs)
            return {
                "choices": [{"message": {"content": "Synthetic summary."}}],
                "usage": {
                    "prompt_tokens": 3,
                    "completion_tokens": 2,
                    "total_tokens": 5,
                },
            }

    monkeypatch.setattr(settings, "summarization_provider", "local")
    monkeypatch.setattr(local_inference_engine, "_get_model", lambda: FakeModel())
    monkeypatch.setattr(
        local_provider_module,
        "format_prompt",
        lambda transcript, format: transcript,
    )
    get_summarization_provider.cache_clear()
    request.addfinalizer(get_summarization_provider.cache_clear)

    response = TestClient(app).post(
        "/summarize",
        json={
            "transcript": "Synthetic follow-up information only.",
            "format": "narrative",
        },
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "Synthetic summary."
    assert response.json()["provider"] == "local"
    assert captured_arguments["top_p"] == 0.9
    assert captured_arguments["repeat_penalty"] == 1.1