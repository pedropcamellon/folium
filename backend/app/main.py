"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Healthcare platform backend with AI capabilities",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION, "app": settings.APP_NAME}


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} starting...")
    print(f"📚 API documentation available at: /docs")

    # Initialize storage service (creates bucket if not exists)
    from app.services.storage import get_storage

    try:
        storage = await get_storage()
        print(
            f"✅ Storage initialized: {storage.config.provider.upper()} - {storage.config.bucket}"
        )
    except Exception as e:
        print(f"⚠️  Storage initialization failed: {e}")

    # Check transcription service health
    from app.services.transcription_service import get_transcription_service

    try:
        transcription_svc = get_transcription_service()
        health = await transcription_svc.health_check()
        if health.get("status") == "healthy":
            provider = health.get("provider", "unknown")
            print(f"✅ Transcription service healthy: {provider}")
        else:
            print(f"⚠️  Transcription service unhealthy: {health.get('error', 'Unknown')}")
    except Exception as e:
        print(f"⚠️  Transcription service unavailable: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print(f"👋 {settings.APP_NAME} shutting down...")
