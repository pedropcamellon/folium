"""AWS Bedrock provider for summarization using Claude."""

import json
import logging
import time
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

from app.providers.base import SummarizationProvider
from app.config import settings
from app.prompts import format_prompt

logger = logging.getLogger(__name__)


class BedrockProvider(SummarizationProvider):
    """AWS Bedrock provider for clinical summarization.

    Uses Claude 3 models (Sonnet/Haiku) via AWS Bedrock.
    Requires AWS credentials and Bedrock model access.
    """

    def __init__(self):
        """Initialize Bedrock client."""
        self._model_id = settings.aws_bedrock_model
        self._temperature = settings.aws_bedrock_temperature
        self._max_tokens = settings.aws_bedrock_max_tokens
        
        # Initialize boto3 client
        try:
            self._client = boto3.client(
                service_name="bedrock-runtime",
                region_name=settings.aws_region,
            )
            logger.info(
                f"[INIT] AWS Bedrock provider initialized (model: {self._model_id}, region: {settings.aws_region})"
            )
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Bedrock client: {e}")
            raise

    async def summarize(
        self, transcript: str, interaction_type: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate clinical summary using Claude via Bedrock.

        Args:
            transcript: Clinical transcript to summarize
            interaction_type: Optional interaction type
            **kwargs: Additional parameters

        Returns:
            Dictionary with summary, structured_data, processing_time, model_used, usage
        """
        logger.info(
            f"[PROC] Starting Bedrock summarization (model: {self._model_id}, transcript length: {len(transcript)} chars)"
        )
        start = time.time()

        # Format prompt
        format_type = kwargs.get("format", "soap")
        prompt = format_prompt(transcript, format=format_type)

        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self._max_tokens,
                "temperature": self._temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "system": "You are a clinical documentation assistant. Always respond with valid JSON only.",
            }

            # Call Bedrock API
            response = self._client.invoke_model(
                modelId=self._model_id,
                body=json.dumps(request_body),
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            
            # Extract content from Claude response
            content = response_body.get("content", [])
            if content and len(content) > 0:
                raw_response = content[0].get("text", "")
            else:
                raise ValueError("Empty response from Bedrock")

            logger.debug(f"[DEBUG] Raw Bedrock response length: {len(raw_response)}")
            logger.debug(f"[DEBUG] Raw Bedrock response: {raw_response[:500]}")

            # Parse JSON response
            try:
                structured_data = json.loads(raw_response)
                logger.debug(
                    f"[DEBUG] Successfully parsed JSON with keys: {structured_data.keys()}"
                )
            except json.JSONDecodeError as e:
                logger.warning(f"[WARN] Failed to parse JSON response: {e}")
                logger.error(f"[ERROR] Failed JSON content: {raw_response}")
                # Fallback: use raw response
                structured_data = {
                    "chief_complaint": "",
                    "subjective": raw_response[:500],
                    "objective": "",
                    "assessment": "",
                    "plan": "",
                    "clinical_tags": [],
                    "icd_codes": [],
                    "action_items": [],
                }

            processing_time = time.time() - start

            # Generate summary text
            if format_type == "soap":
                summary_parts = []
                if structured_data.get("chief_complaint"):
                    summary_parts.append(f"CC: {structured_data['chief_complaint']}")
                if structured_data.get("assessment"):
                    summary_parts.append(structured_data["assessment"])
                if structured_data.get("plan"):
                    summary_parts.append(f"Plan: {structured_data['plan']}")
                summary = " | ".join(summary_parts) if summary_parts else raw_response[:200]
            else:
                summary = raw_response

            logger.info(f"[OK] Bedrock summarization complete in {processing_time:.2f}s")
            logger.debug(f"[DEBUG] Summary preview: {summary[:100]}...")

            # Extract usage metrics
            usage_info = response_body.get("usage", {})

            return {
                "summary": summary,
                "structured_data": structured_data,
                "processing_time": processing_time,
                "model_used": self._model_id,
                "usage": {
                    "prompt_tokens": usage_info.get("input_tokens", 0),
                    "completion_tokens": usage_info.get("output_tokens", 0),
                    "total_tokens": usage_info.get("input_tokens", 0) + usage_info.get("output_tokens", 0),
                },
            }

        except ClientError as e:
            processing_time = time.time() - start
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(
                f"[ERROR] Bedrock API error after {processing_time:.2f}s: {error_code} - {error_msg}",
                exc_info=True,
            )
            raise Exception(f"AWS Bedrock API error: {error_code} - {error_msg}")

        except Exception as e:
            processing_time = time.time() - start
            logger.error(
                f"[ERROR] Bedrock summarization failed after {processing_time:.2f}s: {e}",
                exc_info=True,
            )
            raise

    def get_model_name(self) -> str:
        """Return the Bedrock model ID."""
        return self._model_id

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "bedrock"
