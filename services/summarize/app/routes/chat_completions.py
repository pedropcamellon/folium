"""OpenAI-compatible chat completion routes for the local inference runtime."""

import time
from uuid import uuid4

from app.config import settings
from app.inference.local import local_inference_engine
from app.models import ChatCompletionsRequest
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/v1", tags=["openai-compatible"])


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionsRequest) -> dict:
    """Expose the local model through the OpenAI chat-completions API subset."""
    if settings.summarization_provider != "local":
        raise HTTPException(
            status_code=400,
            detail="Chat completions require the local on-prem provider",
        )
    if request.model != settings.local_model_name:
        raise HTTPException(status_code=400, detail="Requested model is not available")

    try:
        started_at = time.time()
        response = local_inference_engine.chat_completion(
            messages=[message.model_dump() for message in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )
        choice = response["choices"][0]
        return {
            "id": f"chatcmpl-{uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": settings.local_model_name,
            "choices": [
                {
                    "index": 0,
                    "message": choice["message"],
                    "finish_reason": choice.get("finish_reason", "stop"),
                }
            ],
            "usage": response.get("usage"),
            "processing_time": time.time() - started_at,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Local chat completion failed"
        ) from exc
