"""FastAPI application for clinical summarization service."""

import logging
import traceback
from contextlib import asynccontextmanager

from app.config import settings
from app.models import (
    ErrorResponse,
    HealthResponse,
    StructuredSummary,
    SummarizeRequest,
    SummarizeResponse,
)
from app.providers import get_summarization_provider
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info(
        f"[STARTUP] Starting {settings.service_name} service on port {settings.service_port}"
    )
    logger.info(f"[INIT] Provider: {settings.summarization_provider}")

    # Note: Provider is lazy-loaded on first request (avoids healthcheck delays)

    yield

    logger.info("[SHUTDOWN] Shutting down summarization service")


app = FastAPI(
    title="Clinical Summarization Service",
    description="Microservice for generating structured clinical summaries from transcripts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={
        200: {"description": "Successfully generated summary"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Summarization failed"},
    },
)
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """Generate structured clinical summary from transcript.

    Accepts a clinical transcript and returns a structured SOAP note
    with extracted clinical information.

    Args:
        request: SummarizeRequest with transcript and optional parameters

    Returns:
        SummarizeResponse with summary, structured data, and metadata

    Raises:
        HTTPException: If summarization fails
    """
    try:
        logger.info(
            f"[REQUEST] Received summarization request (format: {request.format})"
        )
        logger.debug(f"[DEBUG] Transcript length: {len(request.transcript)} chars")

        if not request.transcript or not request.transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")

        # Get provider (cached singleton)
        provider = get_summarization_provider()

        # Generate summary
        result = await provider.summarize(
            transcript=request.transcript,
            interaction_type=request.interaction_type,
            format=request.format,
        )

        # Debug logging
        logger.debug(f"[DEBUG] Raw result keys: {result.keys()}")
        logger.debug(f"[DEBUG] Summary length: {len(result.get('summary', ''))}")
        logger.debug(f"[DEBUG] Structured data: {result.get('structured_data', {})}")

        # Build response with error handling
        try:
            structured_data = StructuredSummary(**result["structured_data"])
        except Exception as e:
            logger.error(f"[ERROR] Failed to parse structured data: {e}")
            logger.error(f"[ERROR] Raw structured_data: {result['structured_data']}")
            # Create minimal valid response
            structured_data = StructuredSummary(
                chief_complaint=result.get("summary", "")[:200],
                subjective="Parsing failed",
                objective="",
                assessment="",
                plan="See raw summary",
            )

        response = SummarizeResponse(
            summary=result["summary"],
            structured_data=structured_data,
            processing_time=result["processing_time"],
            model_used=result["model_used"],
            provider=provider.get_provider_name(),
            usage=result.get("usage"),
        )

        logger.info(f"[OK] Summarization complete ({result['processing_time']:.2f}s)")
        logger.info(f"[DEBUG] Response summary length: {len(response.summary)}")
        logger.info(
            f"[DEBUG] Response structured_data: chief_complaint={response.structured_data.chief_complaint[:50] if response.structured_data.chief_complaint else 'None'}..."
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Summarization failed: {e}")
        logger.error(traceback.format_exc())

        # Try to get provider info for error response
        try:
            provider = get_summarization_provider()
            model_used = provider.get_model_name()
        except:
            model_used = None

        raise HTTPException(
            status_code=500,
            detail={
                "error": "SummarizationError",
                "detail": str(e),
                "model_used": model_used,
            },
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    responses={200: {"description": "Service is healthy"}},
)
async def health() -> HealthResponse:
    """Health check endpoint.

    Returns service status, provider name, and model name.
    Does NOT trigger model loading (lazy initialization).

    Returns:
        HealthResponse with status, provider, and model
    """
    try:
        # Don't load provider here to avoid healthcheck delays
        # Just return configuration
        return HealthResponse(
            status="healthy",
            provider=settings.summarization_provider,
            model=settings.local_model_name
            if settings.summarization_provider == "local"
            else "configured",
        )
    except Exception as e:
        logger.error(f"[ERROR] Health check failed: {e}")
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


@app.head("/health")
async def health_head():
    """Lightweight health check for Docker HEALTHCHECK.

    Returns 200 OK with no body for quick Docker healthcheck.
    """
    return JSONResponse(content=None, status_code=200)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "provider": settings.summarization_provider,
        "endpoints": {"summarize": "POST /summarize", "health": "GET /health"},
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)
