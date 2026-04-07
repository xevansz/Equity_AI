"""
Backend WebSocket stream for live market data

Endpoint: ws://localhost:8000/ws/stream

Broadcasts:
  - quote: Real-time price updates
  - candle: OHLCV candle data
"""
#app/api/ws_stream.py
import asyncio
import logging
import random
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active connections
active_connections: dict = {}

router = APIRouter(prefix="/api", tags=["WebSocket"])


@router.websocket("/ws/stream")
async def stream_data(ws: WebSocket):
    """
    WebSocket endpoint for live market data streaming.
    
    Sends quote and candle updates every 2 seconds.
    """
    await ws.accept()
    
    client_id = f"{ws.client.host}:{ws.client.port}" if ws.client else "unknown"
    active_connections[client_id] = ws
    logger.info(f"[WebSocket] Client connected: {client_id}")
    
    symbol = "AAPL"
    price = 270.0
    
    try:
        while True:
            # Simulate realistic price movement
            price_change = (random.random() - 0.5) * 2  # ±1 point
            price = max(265, min(280, price + price_change))  # Keep in range
            change = round(price - 268.7, 2)  # Relative to opening
            change_percent = round((change / 268.7) * 100, 2)
            
            # Send quote update
            await ws.send_json({
                "type": "quote",
                "symbol": symbol,
                "data": {
                    "symbol": symbol,
                    "price": round(price, 2),
                    "change": change,
                    "change_percent": change_percent,
                    "timestamp": datetime.utcnow().isoformat(),
                    "volume": random.randint(50000, 500000)
                }
            })
            
            # Send candle data
            await ws.send_json({
                "type": "candle",
                "symbol": symbol,
                "data": {
                    "symbol": symbol,
                    "timestamp": datetime.utcnow().isoformat(),
                    "open": round(price - random.random() * 2, 2),
                    "high": round(price + random.random() * 1.5, 2),
                    "low": round(price - random.random() * 1.5, 2),
                    "close": round(price, 2),
                    "volume": random.randint(50000, 500000)
                }
            })
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client disconnected: {client_id}")
        active_connections.pop(client_id, None)
    except Exception as e:
        logger.error(f"[WebSocket] Error: {e}")
        active_connections.pop(client_id, None)
        await ws.close()


@router.get("/ws/health", include_in_schema=False)
async def ws_health():
    """Health check for WebSocket service"""
    return {
        "status": "ok",
        "active_connections": len(active_connections)
    }
