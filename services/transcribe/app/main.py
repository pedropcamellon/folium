"""FastAPI application for audio transcription microservice"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.models import (
    TranscriptionRequest,
    TranscriptionResponse,
    ErrorResponse,
    HealthResponse,
)
from app.providers import get_transcription_provider
from app.config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize provider on startup"""
    logger.info(
        f"🚀 Starting transcription service with provider: {settings.TRANSCRIPTION_PROVIDER}"
    )

    try:
        provider = await get_transcription_provider()
        logger.info(f"✅ Provider initialized: {provider.get_provider_name()}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize provider: {e}")
        raise

    yield

    logger.info("🛑 Shutting down transcription service")


# Create FastAPI app
app = FastAPI(
    title="Audio Transcription Microservice",
    description="Vendor-agnostic audio transcription with Abstract Provider Pattern",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio from presigned URL.

    Accepts audio from any storage provider (S3, Azure Blob, MinIO).
    Uses configured provider (Whisper, AWS, or Azure) based on TRANSCRIPTION_PROVIDER env var.
    """
    try:
        logger.info(f"📝 Transcription request: {request.audio_url[:50]}...")

        provider = await get_transcription_provider()

        result = await provider.transcribe(
            audio_url=request.audio_url,
            language_code=request.language_code,
            speaker_labels=request.speaker_labels,
            vocabulary_name=request.vocabulary_name,
        )

        logger.info(f"✅ Transcription completed in {result['processing_time']:.2f}s")

        return TranscriptionResponse(**result)

    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(error="Transcription failed", detail=str(e)).dict(),
        )


@app.get("/health", response_model=HealthResponse)
@app.head("/health")
async def health_check():
    """Health check endpoint for container orchestration (supports GET and HEAD)"""
    try:
        provider = await get_transcription_provider()

        return HealthResponse(
            status="healthy",
            provider=provider.get_provider_name(),
            model=settings.WHISPER_MODEL_SIZE
            if settings.TRANSCRIPTION_PROVIDER == "whisper"
            else None,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Audio Transcription Microservice",
        "provider": settings.TRANSCRIPTION_PROVIDER,
        "version": "1.0.0",
        "docs": "/docs",
    }
