"""Summarization endpoints - test integration with summarization service"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.services.summarization_service import SummarizationService
from app.dependencies import get_summarization_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summarization", tags=["summarization"])


class SummarizeRequest(BaseModel):
    """Request model for summarization"""

    transcript: str
    format: str = "soap"
    interaction_type: str | None = None
    language: str = "en"


@router.post("")
async def summarize_transcript(
    request: SummarizeRequest,
    _: object = Depends(require_permission(Permission.INTERACTIONS_SUMMARIZE)),
    service: SummarizationService = Depends(get_summarization_service),
):
    """
    Generate a clinical summary from transcript text.
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
    _: object = Depends(require_permission(Permission.ADMIN_HEALTH_READ)),
    service: SummarizationService = Depends(get_summarization_service),
):
    """Check if summarization service is reachable"""
    is_healthy = await service.health_check()
    return {
        "service": "summarization",
        "status": "healthy" if is_healthy else "unhealthy",
        "url": service.base_url,
    }
