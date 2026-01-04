"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler"""
    # Startup
    print(f"[STARTUP] {settings.APP_NAME} v{settings.VERSION} starting...")
    print("[STARTUP] API documentation available at: /docs")

    # Initialize storage service (creates bucket if not exists)
    from app.services.storage import get_storage

    try:
        storage = await get_storage()
        print(
            f"[STARTUP] Storage initialized: {storage.config.provider.upper()} - {storage.config.bucket}"
        )
    except Exception as e:
        print(f"[WARNING] Storage initialization failed: {e}")

    # Check transcription service health
    from app.services.transcription_service import get_transcription_service

    try:
        transcription_svc = get_transcription_service()
        health = await transcription_svc.health_check()
        if health.get("status") == "healthy":
            provider = health.get("provider", "unknown")
            print(f"[STARTUP] Transcription service healthy: {provider}")
        else:
            print(f"[WARNING] Transcription service unhealthy: {health.get('error', 'Unknown')}")
    except Exception as e:
        print(f"[WARNING] Transcription service unavailable: {e}")

    yield

    # Shutdown
    print(f"[SHUTDOWN] {settings.APP_NAME} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Healthcare platform backend with AI capabilities",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with v1 prefix
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION, "app": settings.APP_NAME}
