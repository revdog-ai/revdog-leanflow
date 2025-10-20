"""Live trading endpoints and WebSocket."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
import asyncio
from datetime import datetime

router = APIRouter()
logger = structlog.get_logger()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        self.active_connections.remove(websocket)
        logger.info(
            "WebSocket client disconnected", total_connections=len(self.active_connections)
        )

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Error broadcasting to client", error=str(e))


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trading data.
    
    Streams:
    - Portfolio value
    - Current P&L
    - Open positions
    - Recent trades
    - OPS counter
    - Compliance alerts
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # TODO: Fetch real-time data from trading engine
            # Mock data for now
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "portfolio_value": 105250.00,
                "pnl": 2350.00,
                "open_positions": 1,
                "ops_counter": 3,
                "kill_switch_active": False,
            }
            
            await websocket.send_json(data)
            await asyncio.sleep(1)  # Update every second
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        manager.disconnect(websocket)


@router.post("/kill-switch")
async def trigger_kill_switch():
    """Emergency stop - liquidate all positions."""
    logger.warning("Kill switch triggered manually")
    
    # TODO: Implement actual liquidation logic
    
    # Broadcast alert to all WebSocket clients
    await manager.broadcast({
        "type": "alert",
        "level": "critical",
        "message": "Kill switch activated - liquidating all positions",
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    return {
        "status": "success",
        "data": {"message": "Kill switch activated", "liquidated_positions": 1},
        "error": None,
    }


@router.get("/status")
async def get_trading_status():
    """Get current trading status."""
    logger.info("Fetching trading status")
    
    # TODO: Fetch from trading engine
    
    return {
        "status": "success",
        "data": {
            "trading_active": False,
            "mode": "paper",  # paper, live
            "connected_clients": len(manager.active_connections),
            "ops_counter": 0,
            "kill_switch_active": False,
        },
        "error": None,
    }

