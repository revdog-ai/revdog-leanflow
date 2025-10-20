"""Backtest endpoints."""

from typing import Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from backend.services.lean_backtest_service import LEANBacktestService

router = APIRouter()
logger = structlog.get_logger()
backtest_service = LEANBacktestService()  # Using LEAN engine


class BacktestRequest(BaseModel):
    """Backtest request model."""

    symbol: str = Field(..., description="Trading symbol (e.g., RELIANCE)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    vwap_window: int = Field(100, ge=10, le=500, description="VWAP window size")
    twap_slices: int = Field(10, ge=5, le=20, description="TWAP slices")
    order_size: int = Field(10, ge=1, description="Order size")
    initial_capital: float = Field(100000.0, gt=0, description="Initial capital")


class BacktestResponse(BaseModel):
    """Backtest response model."""

    run_id: str
    sharpe_ratio: float
    total_return: float
    max_drawdown: float
    win_rate: float
    total_trades: int


@router.post("/run", response_model=dict)
async def run_backtest(request: BacktestRequest):
    """
    Run a backtest with specified parameters.
    
    This endpoint triggers a backtest execution using the LEAN engine
    with the provided strategy parameters.
    """
    logger.info("Backtest requested", symbol=request.symbol, params=request.dict())
    
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        # Run backtest
        run_id = await backtest_service.run_backtest(
            symbol=request.symbol,
            start_date=start_date,
            end_date=end_date,
            vwap_window=request.vwap_window,
            twap_slices=request.twap_slices,
            order_size=request.order_size,
            initial_capital=request.initial_capital,
        )
        
        return {
            "status": "success",
            "data": {
                "run_id": run_id,
                "message": "Backtest completed",
                "estimated_time": "30 seconds",
            },
            "error": None,
        }
    except ValueError as e:
        logger.error("Invalid backtest parameters", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Backtest execution failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/results/{run_id}")
async def get_backtest_results(run_id: str):
    """Get backtest results by run ID."""
    logger.info("Fetching backtest results", run_id=run_id)
    
    try:
        results = await backtest_service.get_results(run_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Backtest run {run_id} not found")
        
        return {
            "status": "success",
            "data": results,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch backtest results", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


@router.get("/list")
async def list_backtests(limit: int = 10, offset: int = 0):
    """List recent backtest runs."""
    logger.info("Listing backtests", limit=limit, offset=offset)
    
    try:
        backtests = await backtest_service.list_backtests(limit=limit, offset=offset)
        
        return {
            "status": "success",
            "data": {
                "backtests": backtests,
                "total": len(backtests),
                "limit": limit,
                "offset": offset,
            },
            "error": None,
        }
    except Exception as e:
        logger.error("Failed to list backtests", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list backtests: {str(e)}")

