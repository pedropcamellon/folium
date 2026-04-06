"""FastAPI application entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.auth import auth_router, users_router
from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import setup_structured_logging
from app.core.metrics import PrometheusMiddleware, metrics_endpoint
from app.core.middleware import CorrelationMiddleware

# Set up structured JSON logging with audit support
logger = setup_structured_logging("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler"""
    # Startup
    logger.info(f"{settings.APP_NAME} v{settings.VERSION} starting...")
    logger.info("API documentation available at: /docs")

    # Initialize database tables
    from app.core.database import async_session_maker, create_db_and_tables

    await create_db_and_tables()

    # Seed test data
    try:
        from app.seed import seed_documents, seed_interactions, seed_patients, seed_users

        async with async_session_maker() as session:
            await seed_users(session)
            patients = await seed_patients(session)
            if patients:
                interactions = await seed_interactions(session, patients)
                await seed_documents(session, patients, interactions)
        logger.info("Database seeding complete")
    except Exception as e:
        logger.warning(f"Failed to seed database: {e}")

    # Initialize storage service (creates bucket if not exists)
    from app.services.storage import get_storage

    try:
        storage = await get_storage()
        logger.info(
            f"Storage initialized: {storage.config.provider.upper()} - {storage.config.bucket}"
        )
    except Exception as e:
        logger.warning(f"Storage initialization failed: {e}")

    # Check transcription service health
    from app.services.transcription_service import get_transcription_service

    try:
        transcription_svc = get_transcription_service()
        health = await transcription_svc.health_check()
        if health.get("status") == "healthy":
            provider = health.get("provider", "unknown")
            logger.info(f"Transcription service healthy: {provider}")
        else:
            logger.warning(f"Transcription service unhealthy: {health.get('error', 'Unknown')}")
    except Exception as e:
        logger.warning(f"Transcription service unavailable: {e}")

    yield

    # Shutdown
    logger.info(f"{settings.APP_NAME} shutting down...")


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

# Correlation ID middleware for request tracing
app.add_middleware(CorrelationMiddleware)

# Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Include API router with v1 prefix
app.include_router(api_router, prefix="/api/v1")

# Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION, "app": settings.APP_NAME}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()
