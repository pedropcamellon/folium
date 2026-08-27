"""Generic local GGUF inference runtime for OpenAI-compatible callers."""

import logging
import time
from typing import Any

from app.config import settings
from llama_cpp import Llama

logger = logging.getLogger(__name__)


class LocalInferenceEngine:
    """Lazily loads the configured local model and serves generic chat completions."""

    def __init__(self) -> None:
        self._model: Llama | None = None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        model = self._get_model()
        return model.create_chat_completion(
            messages=messages,
            temperature=temperature
            if temperature is not None
            else settings.local_temperature,
            max_tokens=max_tokens or settings.local_max_tokens,
            top_p=0.9,
            repeat_penalty=1.1,
            response_format=response_format,
        )

    def _get_model(self) -> Llama:
        if self._model is not None:
            return self._model

        if not settings.local_model_path:
            raise ValueError("LOCAL_MODEL_PATH environment variable not set")

        logger.info("Loading local model from %s", settings.local_model_path)
        started_at = time.time()
        self._model = Llama(
            model_path=settings.local_model_path,
            n_ctx=settings.local_n_ctx,
            n_threads=settings.local_n_threads,
            n_batch=512,
            use_mmap=True,
            use_mlock=False,
            verbose=False,
        )
        logger.info("Loaded local model in %.2fs", time.time() - started_at)
        return self._model


local_inference_engine = LocalInferenceEngine()
