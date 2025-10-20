"""Health check endpoints."""

from fastapi import APIRouter
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "success",
        "data": {
            "service": "revdog-leanflow",
            "status": "healthy",
            "version": "0.1.0",
        },
        "error": None,
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"status": "success", "data": "pong", "error": None}

