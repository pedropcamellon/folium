"""FastAPI application for clinical summarization service."""

import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.routes.chat_completions import router as chat_completions_router
from app.routes.health import router as health_router
from app.routes.summarization import router as summarization_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(chat_completions_router)
app.include_router(summarization_router)
app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)
