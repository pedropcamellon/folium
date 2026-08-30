"""Operational routes for the local inference service."""

from app.config import settings
from app.models import HealthResponse
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=["operations"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return configured provider information without loading the model."""
    return HealthResponse(
        status="healthy",
        provider=settings.summarization_provider,
        model=settings.local_model_name
        if settings.summarization_provider == "local"
        else "configured",
    )


@router.head("/health")
async def health_head() -> Response:
    return Response(status_code=200)


@router.get("/")
async def root() -> dict:
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "provider": settings.summarization_provider,
        "endpoints": {
            "chat_completions": "POST /v1/chat/completions",
            "health": "GET /health",
            "summarize": "POST /summarize",
        },
    }


@router.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)