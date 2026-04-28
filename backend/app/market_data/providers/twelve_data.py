"""
app/market_data/providers/twelve_data.py

Twelve Data API provider — US market quotes, OHLCV time-series.
Uses KeyRotatorRegistry for automatic key rotation on 429 errors.
Uses BaseMCP pattern for connection pooling, caching, and circuit breaker.
"""

import logging
from typing import Any

import httpx

from app.market_data.key_rotator import KeyRotatorRegistry
from app.mcp.base import BaseMCP, CircuitOpenError
from app.schemas.market import Market, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)

BASE_URL = "https://api.twelvedata.com"
TIMEOUT = 12.0  # seconds

# Connection pool limits for TwelveData API
# - max_connections: Total concurrent connections (per host)
# - max_keepalive_connections: Idle connections held open for reuse
# - keepalive_expiry: How long to keep idle connections alive
CONNECTION_LIMITS = httpx.Limits(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=60.0,
)

# Exchange code mapping: internal -> TwelveData
_EXCHANGE_MAP = {
    "NSE": "XNSE",
    "NSE_EQ": "XNSE",
    "BSE": "XBSE",
    "BSE_EQ": "XBSE",
    "NASDAQ": "NASDAQ",
    "NYSE": "NYSE",
}


def _map_exchange(exchange: str | None) -> str | None:
    """Map internal exchange code to TwelveData format."""
    if not exchange:
        return None
    return _EXCHANGE_MAP.get(exchange.upper(), exchange.upper())


def _detect_market_from_exchange(exchange: str | None) -> Market:
    """Detect market from exchange code."""
    if not exchange:
        return Market.US
    exchange_upper = exchange.upper()
    if exchange_upper in ("NSE", "NSE_EQ", "BSE", "BSE_EQ"):
        return Market.INDIA
    return Market.US


class TwelveDataProvider(BaseMCP):
    """
    Twelve Data API provider with connection pooling, caching, circuit breaker,
    and automatic key rotation via KeyRotatorRegistry.

    Uses BaseMCP for:
        - Connection pooling (reuses TCP connections)
        - TTL caching (avoid redundant API calls)
        - Retry/backoff with circuit breaker

    Key rotation is handled per-request via KeyRotatorRegistry.

    Supported endpoints:
        - get_quote()        → StockQuote
        - get_time_series()  → List[OHLCVPoint]
        - get_fundamentals() → Dict (raw, parsed by caller)
    """

    # Override BaseMCP tunables for TwelveData
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
        if not KeyRotatorRegistry.twelve_data:
            logger.error("[TwelveData] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return None
        return KeyRotatorRegistry.twelve_data.get_key()

    def _handle_rate_limit(self, key: str) -> bool:
        """
        Handle rate limit by rotating key.
        Returns True if a new key is available, False otherwise.
        """
        KeyRotatorRegistry.twelve_data.mark_exhausted(key)
        new_key = KeyRotatorRegistry.twelve_data.get_key()
        if not new_key:
            logger.error("[TwelveData] All keys exhausted, cannot retry.")
            return False
        return True

    async def get_quote(self, symbol: str, exchange: str | None = None) -> StockQuote | None:
        """Fetch real-time quote. Returns None on error."""
        key = self._get_key()
        if not key:
            logger.error("[TwelveData] No available API key.")
            return None

        params: dict[str, Any] = {"symbol": symbol, "apikey": key}
        twelve_exchange = _map_exchange(exchange)
        if twelve_exchange:
            params["exchange"] = twelve_exchange

        cache_key = self._cache_key(f"{BASE_URL}/quote", params)
        cached = self._cache_get(cache_key)
        if cached is not None:
            # Parse cached response
            return self._parse_quote_response(cached, symbol, exchange)

        try:
            data = await self.get("/quote", params)
            return self._parse_quote_response(data, symbol, exchange)

        except CircuitOpenError:
            logger.warning(f"[TwelveData] Circuit open for {symbol}")
            return None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                logger.warning("[TwelveData] 429 received — rotating key.")
                if self._handle_rate_limit(key):
                    return await self.get_quote(symbol, exchange)
            logger.error(f"[TwelveData] HTTP error for {symbol}: {exc}")
            return None
        except httpx.TimeoutException:
            logger.error(f"[TwelveData] Timeout fetching quote for {symbol}")
            return None
        except Exception as exc:
            logger.exception(f"[TwelveData] Unexpected error for {symbol}: {exc}")
            return None

    def _parse_quote_response(self, data: dict, symbol: str, exchange: str | None) -> StockQuote | None:
        """Parse TwelveData quote response, handling error cases."""
        # Handle provider-level rate limit in response body
        if data.get("code") == 429:
            logger.warning(f"[TwelveData] API error in body: {data.get('message')}")
            # Try to rotate and fail (can't retry here as we don't have the key context)
            return None

        if data.get("status") == "error":
            msg = data.get("message", "<no message>")
            # messages we do NOT treat as rotation-worthy
            non_rotating = [
                "apikey",
                "incorrect",
                "not specified",
                "grow plan",
                "upgrade",
            ]
            if any(term in msg.lower() for term in non_rotating):
                logger.error(f"[TwelveData] API returned error (no rotate): {msg}")
                return None
            logger.warning(f"[TwelveData] API error in body: {msg} (would rotate if retrying)")
            return None

        market = _detect_market_from_exchange(exchange)
        return StockQuote(
            symbol=data.get("symbol", symbol).upper(),
            price=float(data.get("close") or 0),
            change=float(data.get("change") or 0),
            change_percent=float(data.get("percent_change") or 0),
            volume=int(data.get("volume") or 0),
            high=float(data.get("high") or 0),
            low=float(data.get("low") or 0),
            open=float(data.get("open") or 0),
            prev_close=float(data.get("previous_close") or 0),
            timestamp=data.get("datetime", ""),
            market=market,
        )

    async def get_time_series(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
        exchange: str | None = None,
    ) -> list[OHLCVPoint]:
        """
        Fetch OHLCV time-series.

        interval options: 1min, 5min, 15min, 30min, 45min,
                          1h, 2h, 4h, 1day, 1week, 1month
        """
        key = self._get_key()
        if not key:
            return []

        params: dict[str, Any] = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": key,
        }
        twelve_exchange = _map_exchange(exchange)
        if twelve_exchange:
            params["exchange"] = twelve_exchange

        cache_key = self._cache_key(f"{BASE_URL}/time_series", params)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return self._parse_time_series_response(cached, symbol)

        try:
            data = await self.get("/time_series", params)
            return self._parse_time_series_response(data, symbol)

        except CircuitOpenError:
            logger.warning(f"[TwelveData] Circuit open for {symbol} time-series")
            return []
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                if self._handle_rate_limit(key):
                    return await self.get_time_series(symbol, interval, outputsize, exchange)
            logger.error(f"[TwelveData] HTTP error for {symbol} time-series: {exc}")
            return []
        except Exception as exc:
            logger.exception(f"[TwelveData] Time-series error for {symbol}: {exc}")
            return []

    def _parse_time_series_response(self, data: dict, symbol: str) -> list[OHLCVPoint]:
        """Parse TwelveData time-series response."""
        if "values" not in data:
            logger.warning(f"[TwelveData] No values in time_series response: {data}")
            return []

        return [
            OHLCVPoint(
                timestamp=item["datetime"],
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
                volume=int(item.get("volume", 0)),
            )
            for item in data["values"]
        ]

    async def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        """Fetch fundamentals. Returns raw dict; caller parses."""
        key = self._get_key()
        if not key:
            return {}

        params: dict[str, Any] = {"symbol": symbol, "apikey": key}

        cache_key = self._cache_key(f"{BASE_URL}/statistics", params)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            data = await self.get("/statistics", params)
            return data

        except CircuitOpenError:
            logger.warning(f"[TwelveData] Circuit open for {symbol} fundamentals")
            return {}
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                if self._handle_rate_limit(key):
                    return await self.get_fundamentals(symbol)
            logger.error(f"[TwelveData] HTTP error for {symbol} fundamentals: {exc}")
            return {}
        except Exception as exc:
            logger.exception(f"[TwelveData] Fundamentals error for {symbol}: {exc}")
            return {}
