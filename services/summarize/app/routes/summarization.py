"""Transcript summarization routes."""

import logging

from app.models import (
    ErrorResponse,
    StructuredSummary,
    SummarizeRequest,
    SummarizeResponse,
)
from app.providers import get_summarization_provider
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["summarization"])


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={
        200: {"description": "Successfully generated summary"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Summarization failed"},
    },
)
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """Generate a structured clinical summary from a transcript."""
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    try:
        provider = get_summarization_provider()
        result = await provider.summarize(
            transcript=request.transcript,
            interaction_type=request.interaction_type,
            format=request.format,
        )
        try:
            structured_data = StructuredSummary(**result["structured_data"])
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Structured summary parse failed: %s", exc)
            structured_data = StructuredSummary(
                chief_complaint=result.get("summary", "")[:200],
                subjective="Parsing failed",
                objective="",
                assessment="",
                plan="See raw summary",
            )
        return SummarizeResponse(
            summary=result["summary"],
            structured_data=structured_data,
            processing_time=result["processing_time"],
            model_used=result["model_used"],
            provider=provider.get_provider_name(),
            usage=result.get("usage"),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Summarization failed")
        raise HTTPException(
            status_code=500,
            detail={"error": "SummarizationError", "detail": str(exc)},
        ) from exc