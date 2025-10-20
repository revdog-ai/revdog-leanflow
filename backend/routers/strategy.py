"""Strategy configuration endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field, validator
import structlog

router = APIRouter()
logger = structlog.get_logger()


class StrategyConfig(BaseModel):
    """Strategy configuration model."""

    vwap_window: int = Field(100, ge=10, le=500, description="VWAP window size")
    twap_slices: int = Field(10, ge=5, le=20, description="TWAP slices")
    order_size: int = Field(10, ge=1, description="Order size per trade")
    drawdown_threshold: float = Field(0.05, gt=0, le=0.2, description="Kill switch threshold")
    ops_limit: int = Field(10, ge=1, le=10, description="Orders per second limit")
    
    @validator("vwap_window")
    def validate_vwap_window(cls, v):
        """Validate VWAP window."""
        if v < 10 or v > 500:
            raise ValueError("VWAP window must be between 10 and 500")
        return v


@router.get("/config")
async def get_config():
    """Get current strategy configuration."""
    logger.info("Fetching strategy configuration")
    
    # TODO: Load from config file or database
    
    return {
        "status": "success",
        "data": {
            "vwap_window": 100,
            "twap_slices": 10,
            "order_size": 10,
            "drawdown_threshold": 0.05,
            "ops_limit": 10,
        },
        "error": None,
    }


@router.post("/config")
async def save_config(config: StrategyConfig):
    """Save strategy configuration."""
    logger.info("Saving strategy configuration", config=config.dict())
    
    # TODO: Save to config file or database
    
    return {
        "status": "success",
        "data": {"message": "Configuration saved", "config": config.dict()},
        "error": None,
    }


@router.post("/validate")
async def validate_config(config: StrategyConfig):
    """Validate strategy configuration."""
    logger.info("Validating strategy configuration", config=config.dict())
    
    # Validation happens automatically via Pydantic
    return {
        "status": "success",
        "data": {"valid": True, "config": config.dict()},
        "error": None,
    }

