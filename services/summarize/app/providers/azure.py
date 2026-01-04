"""Azure OpenAI provider for summarization."""

import json
import logging
import time
from typing import Dict, Any, Optional

from openai import AzureOpenAI

from app.providers.base import SummarizationProvider
from app.config import settings
from app.prompts import format_prompt

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(SummarizationProvider):
    """Azure OpenAI provider for clinical summarization.

    Supports any language model deployed in Azure OpenAI Service.
    Requires Azure OpenAI endpoint, API key, and deployment name.
    """

    def __init__(self):
        """Initialize Azure OpenAI client."""
        self._deployment_name = settings.azure_openai_deployment
        self._temperature = settings.azure_openai_temperature
        self._max_tokens = settings.azure_openai_max_tokens

        # Initialize Azure OpenAI client
        try:
            self._client = AzureOpenAI(
                api_key=settings.azure_openai_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
            logger.info(
                f"[INIT] Azure OpenAI provider initialized (deployment: {self._deployment_name}, endpoint: {settings.azure_openai_endpoint})"
            )
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Azure OpenAI client: {e}")
            raise

    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate clinical summary using Azure OpenAI.

        Args:
            transcript: Clinical transcript to summarize
            interaction_type: Type of clinical interaction (optional)
            **kwargs: Additional parameters

        Returns:
            Dictionary with summary, structured_data, processing_time, model_used

        Raises:
            Exception: If Azure API call fails
        """
        start_time = time.time()

        # Format prompt
        prompt = format_prompt(transcript, interaction_type)

        logger.info(
            f"[PROC] Starting Azure OpenAI summarization (deployment: {self._deployment_name}, "
            f"max_tokens: {self._max_tokens}, temperature: {self._temperature})"
        )

        try:
            # Call Azure OpenAI API
            response = self._client.chat.completions.create(
                model=self._deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical documentation specialist. Generate structured SOAP notes from clinical transcripts. Return ONLY valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_completion_tokens=self._max_tokens,
            )

            # Extract response
            if not response.choices or len(response.choices) == 0:
                raise ValueError("No response from Azure OpenAI")

            # Debug: Log full response structure
            logger.debug(f"[DEBUG] Response object: {response}")
            logger.debug(f"[DEBUG] First choice: {response.choices[0]}")
            logger.debug(f"[DEBUG] Message: {response.choices[0].message}")

            content = response.choices[0].message.content
            logger.debug(
                f"[DEBUG] Content type: {type(content)}, length: {len(content) if content else 0}"
            )
            logger.debug(f"[DEBUG] Content value: {repr(content)}")

            processing_time = time.time() - start_time

            # Parse JSON response (handle markdown code blocks)
            try:
                # Try direct JSON parse first
                structured_data = json.loads(content)
            except json.JSONDecodeError:
                # Try extracting JSON from markdown code blocks
                import re

                json_match = re.search(
                    r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL
                )
                if json_match:
                    try:
                        structured_data = json.loads(json_match.group(1))
                        logger.info("[INFO] Extracted JSON from markdown code block")
                    except json.JSONDecodeError as e:
                        logger.warning(f"[WARN] Failed to parse extracted JSON: {e}")
                        logger.debug(f"[DEBUG] Raw content: {content}")
                        structured_data = {
                            "chief_complaint": "Unable to parse",
                            "subjective": content[:200],
                            "objective": "",
                            "assessment": "",
                            "plan": "",
                            "clinical_tags": [],
                            "icd_codes": [],
                            "action_items": [],
                        }
                else:
                    # No markdown code block found, no valid JSON
                    logger.warning(f"[WARN] No JSON found in response")
                    logger.debug(f"[DEBUG] Raw content: {content}")
                    structured_data = {
                        "chief_complaint": "Unable to parse",
                        "subjective": content[:200] if content else "",
                        "objective": "",
                        "assessment": "",
                        "plan": "",
                        "clinical_tags": [],
                        "icd_codes": [],
                        "action_items": [],
                    }

            # Build summary text
            summary = self._build_summary(structured_data)

            # Extract usage info
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            logger.info(
                f"[OK] Azure OpenAI summarization completed in {processing_time:.2f}s "
                f"(tokens: {usage.get('total_tokens', 'N/A')})"
            )

            return {
                "summary": summary,
                "structured_data": structured_data,
                "processing_time": round(processing_time, 2),
                "model_used": self._deployment_name,
                "usage": usage,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"[ERROR] Azure OpenAI API error after {processing_time:.2f}s: {e}"
            )
            raise Exception(f"Azure OpenAI API error: {str(e)}")

    def _build_summary(self, structured_data: Dict[str, Any]) -> str:
        """Build concise summary text from structured data.

        Args:
            structured_data: Parsed SOAP note

        Returns:
            One-line summary string
        """
        cc = structured_data.get("chief_complaint", "N/A")
        assessment = structured_data.get("assessment", "N/A")
        plan = structured_data.get("plan", "N/A")

        return f"CC: {cc} | {assessment} | Plan: {plan}"

    def get_model_name(self) -> str:
        """Return the Azure deployment name."""
        return self._deployment_name

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "azure"
