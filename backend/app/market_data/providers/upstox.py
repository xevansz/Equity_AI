"""
app/market_data/providers/upstox.py

Upstox API v2 provider — Indian market (NSE/BSE) quotes,
OHLCV data, and market depth (order book).
Uses KeyRotatorRegistry for automatic key rotation.
Uses BaseMCP pattern for connection pooling, caching, and circuit breaker.
"""

import logging
from typing import Any

import httpx

from app.market_data.key_rotator import KeyRotatorRegistry
from app.mcp.base import BaseMCP, CircuitOpenError
from app.schemas.market import Market, MarketDepth, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)

BASE_URL = "https://api.upstox.com/v2"
TIMEOUT = 12.0

# Connection pool limits for Upstox API
CONNECTION_LIMITS = httpx.Limits(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=60.0,
)


def _build_instrument_key(symbol: str, exchange: str = "NSE_EQ") -> str:
    """
    Convert plain symbol → Upstox instrument key.
    e.g. "HINDCOPPER" → "NSE_EQ|HINDCOPPER"
    Override exchange for BSE: "BSE_EQ|SYMBOL"
    """
    return f"{exchange}|{symbol.upper()}"


def _auth_headers(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


class UpstoxProvider(BaseMCP):
    """
    Upstox API v2 provider with connection pooling, caching, circuit breaker,
    and automatic key rotation via KeyRotatorRegistry.

    Uses BaseMCP for:
        - Connection pooling (reuses TCP connections)
        - TTL caching (avoid redundant API calls)
        - Retry/backoff with circuit breaker

    Key rotation is handled per-request via KeyRotatorRegistry.
    """

    # Override BaseMCP tunables for Upstox
    CACHE_TTL: float = 30.0  # Shorter cache for real-time market data
    MAX_RETRIES: int = 2  # Fewer retries to fail fast on rate limits

    def __init__(self):
        # Initialize with empty API key - we'll inject from KeyRotatorRegistry per-request
        super().__init__(base_url=BASE_URL, api_key=None)
        # Replace client with connection pooling enabled
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(TIMEOUT, connect=5.0),
            limits=CONNECTION_LIMITS,
        )

    def _get_key(self) -> str | None:
        """Get current API key from KeyRotatorRegistry."""
        if not KeyRotatorRegistry.upstox:
            logger.error("[Upstox] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return None
        return KeyRotatorRegistry.upstox.get_key()

    def _handle_rate_limit(self, key: str) -> bool:
        """
        Handle rate limit by rotating key.
        Returns True if a new key is available, False otherwise.
        """
        KeyRotatorRegistry.upstox.mark_exhausted(key)
        new_key = KeyRotatorRegistry.upstox.get_key()
        if not new_key:
            logger.error("[Upstox] All keys exhausted, cannot retry.")
            return False
        return True

    def _auth_headers(self, key: str) -> dict[str, str]:
        """Build authorization headers for Upstox API."""
        return {"Authorization": f"Bearer {key}", "Accept": "application/json"}

    async def get_quote(self, symbol: str, exchange: str = "NSE_EQ") -> StockQuote | None:
        """Fetch real-time LTP + OHLC quote for an Indian stock."""
        key = self._get_key()
        if not key:
            logger.error("[Upstox] No available API key.")
            return None

        instrument_key = _build_instrument_key(symbol, exchange)
        params: dict[str, Any] = {"instrument_key": instrument_key}

        try:
            data = await self.get(
                "/market-quote/quotes",
                params,
                headers=self._auth_headers(key),
            )

            if data.get("status") != "success":
                logger.warning(f"[Upstox] Non-success status: {data}")
                return None

            q = data["data"].get(instrument_key, {})
            ltp = float(q.get("last_price", 0))
            prev_close = float(q.get("prev_close_price") or q.get("ohlc", {}).get("close", ltp))
            change = ltp - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0.0

            ohlc = q.get("ohlc", {})

            return StockQuote(
                symbol=symbol.upper(),
                price=ltp,
                change=round(change, 2),
                change_percent=round(change_pct, 2),
                volume=int(q.get("volume", 0)),
                high=float(ohlc.get("high", 0)),
                low=float(ohlc.get("low", 0)),
                open=float(ohlc.get("open", 0)),
                prev_close=prev_close,
                timestamp=q.get("last_trade_time", ""),
                market=Market.INDIA,
            )

        except CircuitOpenError:
            logger.warning(f"[Upstox] Circuit open for {symbol}")
            return None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                logger.warning("[Upstox] 429 received — rotating key.")
                if self._handle_rate_limit(key):
                    return await self.get_quote(symbol, exchange)
            if exc.response.status_code == 401:
                logger.error(f"[Upstox] 401 Unauthorized — key …{key[-6:]} may be expired.")
                KeyRotatorRegistry.upstox.mark_exhausted(key)
                return None
            logger.error(f"[Upstox] HTTP error for {symbol}: {exc}")
            return None
        except httpx.TimeoutException:
            logger.error(f"[Upstox] Timeout for {symbol}")
            return None
        except Exception as exc:
            logger.exception(f"[Upstox] Quote error for {symbol}: {exc}")
            return None

    async def get_market_depth(self, symbol: str, exchange: str = "NSE_EQ") -> MarketDepth | None:
        """
        Fetch top-5 bid/ask order book.
        Returns MarketDepth with buy_orders, sell_orders, buy_pct, sell_pct.
        """
        key = self._get_key()
        if not key:
            return None

        instrument_key = _build_instrument_key(symbol, exchange)
        params: dict[str, Any] = {"instrument_key": instrument_key}

        try:
            data = await self.get(
                "/market-quote/quotes",
                params,
                headers=self._auth_headers(key),
            )

            if data.get("status") != "success":
                return None

            q = data["data"].get(instrument_key, {})
            depth = q.get("depth", {})

            buy_orders: list[dict] = depth.get("buy", [])[:5]
            sell_orders: list[dict] = depth.get("sell", [])[:5]

            total_buy_qty = sum(o.get("quantity", 0) for o in buy_orders)
            total_sell_qty = sum(o.get("quantity", 0) for o in sell_orders)
            total_qty = total_buy_qty + total_sell_qty

            return MarketDepth(
                symbol=symbol.upper(),
                buy_orders=buy_orders,
                sell_orders=sell_orders,
                buy_percentage=round((total_buy_qty / total_qty * 100) if total_qty else 0, 2),
                sell_percentage=round((total_sell_qty / total_qty * 100) if total_qty else 0, 2),
            )

        except CircuitOpenError:
            logger.warning(f"[Upstox] Circuit open for {symbol} market depth")
            return None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                if self._handle_rate_limit(key):
                    return await self.get_market_depth(symbol, exchange)
            logger.error(f"[Upstox] HTTP error for {symbol} market depth: {exc}")
            return None
        except Exception as exc:
            logger.exception(f"[Upstox] MarketDepth error for {symbol}: {exc}")
            return None

    async def get_historical(
        self,
        symbol: str,
        interval: str = "1minute",
        exchange: str = "NSE_EQ",
        from_date: str = "",
        to_date: str = "",
    ) -> list[OHLCVPoint]:
        """
        Fetch historical candles from Upstox.
        interval: 1minute, 30minute, 1day, 1week, 1month
        """
        from datetime import date, timedelta

        key = self._get_key()
        if not key:
            return []

        if not to_date:
            to_date = date.today().isoformat()
        if not from_date:
            from_date = (date.today() - timedelta(days=7)).isoformat()

        instrument_key = _build_instrument_key(symbol, exchange)
        endpoint = f"/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

        try:
            data = await self.get(
                endpoint,
                {},
                headers=self._auth_headers(key),
            )

            candles: list[Any] = data.get("data", {}).get("candles", [])

            return [
                OHLCVPoint(
                    timestamp=c[0],
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=int(c[5]),
                )
                for c in candles
            ]

        except CircuitOpenError:
            logger.warning(f"[Upstox] Circuit open for {symbol} historical")
            return []
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                if self._handle_rate_limit(key):
                    return await self.get_historical(symbol, interval, exchange, from_date, to_date)
            logger.error(f"[Upstox] HTTP error for {symbol} historical: {exc}")
            return []
        except Exception as exc:
            logger.exception(f"[Upstox] Historical error for {symbol}: {exc}")
            return []
