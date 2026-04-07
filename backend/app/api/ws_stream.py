"""
Backend WebSocket stream for live market data

Endpoint: ws://localhost:8000/api/ws/stream

Protocol:
  Client sends: {"action": "subscribe", "symbols": ["AAPL", "TSLA"], "market": "US", "interval": "1min"}
  Client sends: {"action": "unsubscribe", "symbols": ["AAPL"]}
  Client sends: {"action": "ping"}

  Server sends: {"type": "quote", "symbol": "AAPL", "data": {...}}
  Server sends: {"type": "candle", "symbol": "AAPL", "data": {...}}
  Server sends: {"type": "pong"}
  Server sends: {"type": "error", "message": "..."}
"""

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.market import Market
from app.utils.market_resolver import resolve_market_from_symbol

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["WebSocket"])

# Store active connections with their subscriptions
active_connections: dict[str, dict] = {}


@router.websocket("/ws/stream")
async def stream_data(ws: WebSocket):
    """
    WebSocket endpoint for live market data streaming.

    Clients can subscribe to multiple symbols and receive real-time updates.
    """
    await ws.accept()

    client_id = f"{ws.client.host}:{ws.client.port}" if ws.client else "unknown"
    active_connections[client_id] = {
        "ws": ws,
        "subscriptions": set(),
        "market": Market.US,
        "interval": "1min",
    }
    logger.info(f"[WebSocket] Client connected: {client_id}")

    # Get dispatcher from app state
    dispatcher = ws.app.state.market_dispatcher

    try:
        # Start background task to send updates
        update_task = asyncio.create_task(send_updates(client_id, dispatcher))

        # Listen for client messages
        while True:
            message = await ws.receive_json()
            action = message.get("action")

            if action == "subscribe":
                symbols = message.get("symbols", [])
                market = message.get("market", "US")
                interval = message.get("interval", "1min")

                active_connections[client_id]["subscriptions"].update(symbols)
                active_connections[client_id]["market"] = Market(market)
                active_connections[client_id]["interval"] = interval

                logger.info(f"[WebSocket] {client_id} subscribed to {symbols}")
                await ws.send_json({"type": "info", "message": f"Subscribed to {len(symbols)} symbols"})

            elif action == "unsubscribe":
                symbols = message.get("symbols", [])
                active_connections[client_id]["subscriptions"].difference_update(symbols)
                logger.info(f"[WebSocket] {client_id} unsubscribed from {symbols}")

            elif action == "ping":
                await ws.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"[WebSocket] Error for {client_id}: {e}")
        await ws.send_json({"type": "error", "message": str(e)})
    finally:
        if update_task:
            update_task.cancel()
        active_connections.pop(client_id, None)
        try:
            await ws.close()
        except Exception:
            pass


async def send_updates(client_id: str, dispatcher):
    """Background task to send real-time updates to a client"""
    while client_id in active_connections:
        try:
            conn = active_connections[client_id]
            ws = conn["ws"]
            subscriptions = conn["subscriptions"]

            if not subscriptions:
                await asyncio.sleep(2)
                continue

            # Fetch quotes for all subscribed symbols
            for symbol in list(subscriptions):
                try:
                    # Resolve market for the symbol
                    resolved_market, exchange, clean_symbol = resolve_market_from_symbol(symbol)

                    # Get quote from dispatcher
                    quote = await dispatcher.get_quote(clean_symbol, resolved_market, exchange.value)

                    if quote:
                        # Send quote update
                        await ws.send_json(
                            {
                                "type": "quote",
                                "symbol": symbol,
                                "data": {
                                    "symbol": quote.symbol,
                                    "price": quote.price,
                                    "change": quote.change,
                                    "change_percent": quote.change_percent,
                                    "volume": quote.volume,
                                    "high": quote.high,
                                    "low": quote.low,
                                    "open": quote.open,
                                    "prev_close": quote.prev_close,
                                    "timestamp": quote.timestamp,
                                    "market": quote.market.value,
                                },
                            }
                        )
                    else:
                        logger.warning(f"[WebSocket] No quote data for {symbol}")

                except Exception as e:
                    logger.error(f"[WebSocket] Error fetching {symbol}: {e}")
                    await ws.send_json(
                        {"type": "error", "symbol": symbol, "message": f"Failed to fetch data: {str(e)}"}
                    )

            # Wait before next update (2 seconds for real-time feel)
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"[WebSocket] Update loop error for {client_id}: {e}")
            break


@router.get("/ws/health", include_in_schema=False)
async def ws_health():
    """Health check for WebSocket service"""
    return {"status": "ok", "active_connections": len(active_connections)}
