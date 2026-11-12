"""Tests for the local OpenAI-compatible chat-completions route."""

from fastapi.testclient import TestClient

from app.config import settings
from app.inference.local import local_inference_engine
from app.main import app


def test_chat_completions_forwards_sampling_parameters(monkeypatch):
    captured_arguments = {}

    class FakeModel:
        def create_chat_completion(self, **kwargs):
            captured_arguments.update(kwargs)
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Synthetic output",
                        }
                    }
                ],
                "usage": {},
            }

    monkeypatch.setattr(settings, "summarization_provider", "local")
    monkeypatch.setattr(settings, "local_model_name", "local-model")
    monkeypatch.setattr(local_inference_engine, "_get_model", lambda: FakeModel())

    response = TestClient(app).post(
        "/v1/chat/completions",
        json={
            "model": "local-model",
            "messages": [{"role": "user", "content": "Synthetic input"}],
            "top_p": 0.75,
            "repeat_penalty": 1.25,
        },
    )

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "Synthetic output"
    assert captured_arguments["top_p"] == 0.75
    assert captured_arguments["repeat_penalty"] == 1.25


def test_chat_completions_uses_sampling_defaults(monkeypatch):
    captured_arguments = {}

    class FakeModel:
        def create_chat_completion(self, **kwargs):
            captured_arguments.update(kwargs)
            return {"choices": [{"message": {"role": "assistant", "content": "Synthetic output"}}]}

    monkeypatch.setattr(settings, "summarization_provider", "local")
    monkeypatch.setattr(settings, "local_model_name", "local-model")
    monkeypatch.setattr(local_inference_engine, "_get_model", lambda: FakeModel())

    response = TestClient(app).post(
        "/v1/chat/completions",
        json={
            "model": "local-model",
            "messages": [{"role": "user", "content": "Synthetic input"}],
        },
    )

    assert response.status_code == 200
    assert captured_arguments["top_p"] == 0.9
    assert captured_arguments["repeat_penalty"] == 1.1


def test_chat_completions_rejects_unsupported_parameters():
    response = TestClient(app).post(
        "/v1/chat/completions",
        json={
            "model": "local-model",
            "messages": [{"role": "user", "content": "Synthetic input"}],
            "seed": 12,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"