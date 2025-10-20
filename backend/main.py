"""
RevDog LeanFlow Backend - FastAPI Application

This module provides the main FastAPI application with REST API endpoints
and WebSocket support for real-time trading data.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from backend.core.config import settings
from backend.routers import backtest, strategy, live_trading, health
from src.database.connection import init_db

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting RevDog LeanFlow backend", version="0.1.0")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    yield
    logger.info("Shutting down RevDog LeanFlow backend")


app = FastAPI(
    title="RevDog LeanFlow API",
    description="Algorithmic Trading System for VWAP/TWAP Strategies",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["Strategy"])
app.include_router(live_trading.router, prefix="/api/trading", tags=["Live Trading"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": "Internal server error" if not settings.DEBUG else str(exc),
        },
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "success",
        "data": {
            "message": "RevDog LeanFlow API",
            "version": "0.1.0",
            "docs": "/docs",
        },
        "error": None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )

