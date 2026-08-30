"""Local LLM provider using llama-cpp-python."""

import json
import logging
import time
from typing import Any

from app.config import settings
from app.inference.local import local_inference_engine
from app.prompts import format_prompt
from app.providers.base import SummarizationProvider
from folium.ai import system_message, user_message

logger = logging.getLogger(__name__)


class LocalLLMProvider(SummarizationProvider):
    """Local LLM provider using llama-cpp-python with GGUF models.

    Supports Llama 3, Mistral, Phi-3, and other GGUF-format models.
    Runs entirely offline with no external API calls.
    """

    def __init__(self):
        """Initialize the local LLM provider.

        Model is loaded lazily on first summarize() call to avoid
        startup delays in Docker healthchecks.
        """
        self._model_name = settings.local_model_name
        logger.info(
            f"[INIT] Local LLM provider initialized (model: {self._model_name})"
        )

    async def summarize(
        self,
        transcript: str,
        interaction_type: str | None = None,
        format: str = "soap",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate clinical summary using local LLM.

        Args:
            transcript: Clinical transcript text
            interaction_type: Type of interaction (currently unused)
            format: Output format ('soap' or 'narrative')
            **kwargs: Additional parameters (ignored)

        Returns:
            Dictionary with summary, structured_data, processing_time, model_used

        Raises:
            ValueError: If model path not configured
            Exception: If generation fails
        """
        logger.info(
            f"[PROC] Starting summarization (transcript length: {len(transcript)} chars)"
        )
        start = time.time()

        # Format prompt with transcript
        prompt = format_prompt(transcript, format=format)

        try:
            # Generate summary with optimized settings
            response = local_inference_engine.chat_completion(
                messages=[
                    system_message("You are a clinical documentation assistant."),
                    user_message(prompt),
                ],
                temperature=settings.local_temperature,
                max_tokens=settings.local_max_tokens,
                top_p=0.9,  # Nucleus sampling for faster generation
                repeat_penalty=1.1,  # Reduce repetition
                response_format={"type": "json_object"} if format == "soap" else None,
            )

            # Extract generated text
            content = response["choices"][0]["message"]["content"]

            logger.debug(f"[DEBUG] Raw LLM response length: {len(content)}")
            logger.debug(f"[DEBUG] Raw LLM response: {content}")

            # Parse JSON if SOAP format
            if format == "soap":
                try:
                    structured_data = json.loads(content)
                    logger.debug(
                        f"[DEBUG] Successfully parsed JSON with keys: {structured_data.keys()}"
                    )
                    # Normalize plan to string (LLM sometimes returns list)
                    if isinstance(structured_data.get("plan"), list):
                        structured_data["plan"] = "\n".join(structured_data["plan"])
                except json.JSONDecodeError as e:
                    logger.warning(f"[WARN] Failed to parse JSON response: {e}")
                    logger.error(f"[ERROR] Failed JSON content: {content}")
                    structured_data = {
                        "chief_complaint": "",
                        "subjective": content[:500],
                        "objective": "",
                        "assessment": "",
                        "plan": "",
                        "clinical_tags": [],
                        "icd_codes": [],
                        "action_items": [],
                    }
            else:
                structured_data = {"narrative": content}

            processing_time = time.time() - start

            # Generate summary text
            if format == "soap":
                summary_parts = []
                if structured_data.get("chief_complaint"):
                    summary_parts.append(f"CC: {structured_data['chief_complaint']}")
                if structured_data.get("assessment"):
                    summary_parts.append(structured_data["assessment"])
                if structured_data.get("plan"):
                    summary_parts.append(f"Plan: {structured_data['plan']}")
                summary = " | ".join(summary_parts) if summary_parts else content[:200]
            else:
                summary = content

            logger.info(f"[OK] Summarization complete in {processing_time:.2f}s")
            logger.debug(f"[DEBUG] Summary preview: {summary[:100]}...")

            return {
                "summary": summary,
                "structured_data": structured_data,
                "processing_time": processing_time,
                "model_used": self._model_name,
                "usage": {
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens"),
                    "completion_tokens": response.get("usage", {}).get(
                        "completion_tokens"
                    ),
                    "total_tokens": response.get("usage", {}).get("total_tokens"),
                },
            }

        except Exception as e:
            processing_time = time.time() - start
            logger.error(
                f"[ERROR] Summarization failed after {processing_time:.2f}s: {e}",
                exc_info=True,
            )
            raise

    def get_model_name(self) -> str:
        """Return the model name."""
        return self._model_name

    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "local"
