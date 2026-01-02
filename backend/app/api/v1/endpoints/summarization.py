"""Summarization endpoints - test integration with summarization service"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.summarization_service import SummarizationService
from app.dependencies import get_summarization_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summarization", tags=["summarization"])


class SummarizeRequest(BaseModel):
    """Request model for summarization"""

    transcript: str
    format: str = "soap"
    interaction_type: Optional[str] = None
    language: str = "en"


@router.post("/test")
async def test_summarization(
    request: SummarizeRequest,
    service: SummarizationService = Depends(get_summarization_service),
):
    """
    Test endpoint to call summarization service directly.

    Use this to verify the integration is working before
    wiring it into the full interaction workflow.
    """
    try:
        result = await service.summarize(
            transcript=request.transcript,
            format=request.format,
            interaction_type=request.interaction_type,
            language=request.language,
        )
        return result

    except Exception as e:
        logger.error(f"[ERROR] Summarization test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_summarization_health(
    service: SummarizationService = Depends(get_summarization_service),
):
    """Check if summarization service is reachable"""
    is_healthy = await service.health_check()
    return {
        "service": "summarization",
        "status": "healthy" if is_healthy else "unhealthy",
        "url": service.base_url,
    }
