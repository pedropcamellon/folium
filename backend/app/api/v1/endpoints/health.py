"""Health check endpoints"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "api_version": "v1"}
