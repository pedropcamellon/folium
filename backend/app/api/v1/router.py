"""Main API router for v1 endpoints"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    patients,
    interactions,
    documents,
    health,
    storage_test,
    summarization,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(patients.router, tags=["patients"])
api_router.include_router(interactions.router, tags=["interactions"])
api_router.include_router(documents.router, tags=["clinical-documents"])
api_router.include_router(storage_test.router, tags=["storage-test"])
api_router.include_router(summarization.router, tags=["summarization"])
