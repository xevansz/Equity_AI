"""
app/market_data/providers/twelve_data.py

Twelve Data API provider — US market quotes, OHLCV time-series.
Uses KeyRotatorRegistry for automatic key rotation on 429 errors.
"""

import logging
from typing import Any

import httpx

from app.market_data.key_rotator import KeyRotatorRegistry
from app.schemas.market import Market, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)

BASE_URL = "https://api.twelvedata.com"
TIMEOUT = 12.0  # seconds


class TwelveDataProvider:
    """
    All methods are static so the provider is stateless.
    API key management is delegated to KeyRotatorRegistry.twelve_data.

    Supported endpoints:
        - get_quote()        → StockQuote
        - get_time_series()  → List[OHLCVPoint]
        - get_fundamentals() → Dict (raw, parsed by caller)
    """

    # ------------------------------------------------------------------
    # Quote
    # ------------------------------------------------------------------

    @staticmethod
    async def get_quote(symbol: str) -> StockQuote | None:
        """Fetch real-time quote. Returns None on error."""
        if not KeyRotatorRegistry.twelve_data:
            logger.error("[TwelveData] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return None
        
        key = KeyRotatorRegistry.twelve_data.get_key()
        if not key:
            logger.error("[TwelveData] No available API key.")
            return None

        params = {"symbol": symbol, "apikey": key}

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.get(f"{BASE_URL}/quote", params=params)

                # Handle rate limit at HTTP layer
                if resp.status_code == 429:
                    logger.warning("[TwelveData] 429 received — rotating key.")
                    KeyRotatorRegistry.twelve_data.mark_exhausted(key)
                    return await TwelveDataProvider.get_quote(symbol)

                resp.raise_for_status()
                data = resp.json()

                # Handle provider-level rate limit in response body. twelve-data sometimes returns
                # a 200 status with ``status": "error"`` when a key is malformed/unauthorised or a
                # symbol is not available on the current plan. We only want to rotate the key when
                # the message indicates a rate‑limit has been hit. Otherwise we log and bail out so
                # callers can fall back to mocks and the bad key remains available for later manual
                # inspection.
                if data.get("code") == 429:
                    # explicit rate limit response
                    logger.warning(f"[TwelveData] API error in body: {data.get('message')}")
                    KeyRotatorRegistry.twelve_data.mark_exhausted(key)
                    return await TwelveDataProvider.get_quote(symbol)

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

                    # any other error we conservatively rotate
                    logger.warning(f"[TwelveData] API error in body: {msg} (rotating key)")
                    KeyRotatorRegistry.twelve_data.mark_exhausted(key)
                    return await TwelveDataProvider.get_quote(symbol)

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
                    market=Market.US,
                )

            except httpx.TimeoutException:
                logger.error(f"[TwelveData] Timeout fetching quote for {symbol}")
                return None
            except Exception as exc:
                logger.exception(f"[TwelveData] Unexpected error for {symbol}: {exc}")
                return None

    # ------------------------------------------------------------------
    # Time Series
    # ------------------------------------------------------------------

    @staticmethod
    async def get_time_series(
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
    ) -> list[OHLCVPoint]:
        """
        Fetch OHLCV time-series.

        interval options: 1min, 5min, 15min, 30min, 45min,
                          1h, 2h, 4h, 1day, 1week, 1month
        """
        if not KeyRotatorRegistry.twelve_data:
            logger.error("[TwelveData] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return []
        
        key = KeyRotatorRegistry.twelve_data.get_key()
        if not key:
            return []

        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": key,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(f"{BASE_URL}/time_series", params=params)

                if resp.status_code == 429:
                    KeyRotatorRegistry.twelve_data.mark_exhausted(key)
                    return await TwelveDataProvider.get_time_series(symbol, interval, outputsize)

                resp.raise_for_status()
                data = resp.json()

                if "values" not in data:
                    # unauthorized / bad key responses show up here as well; don't rotate in that
                    # case because rate limits haven't been consumed.
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

            except Exception as exc:
                logger.exception(f"[TwelveData] Time-series error for {symbol}: {exc}")
                return []

    # ------------------------------------------------------------------
    # Fundamentals (raw dict — parsed by schemas/financial.py)
    # ------------------------------------------------------------------

    @staticmethod
    async def get_fundamentals(symbol: str) -> dict[str, Any]:
        """Fetch fundamentals. Returns raw dict; caller parses."""
        if not KeyRotatorRegistry.twelve_data:
            logger.error("[TwelveData] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return {}
        
        key = KeyRotatorRegistry.twelve_data.get_key()
        if not key:
            return {}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                # Twelve Data statistics endpoint
                resp = await client.get(
                    f"{BASE_URL}/statistics",
                    params={"symbol": symbol, "apikey": key},
                )
                if resp.status_code == 429:
                    KeyRotatorRegistry.twelve_data.mark_exhausted(key)
                    return await TwelveDataProvider.get_fundamentals(symbol)

                resp.raise_for_status()
                return resp.json()

            except Exception as exc:
                logger.exception(f"[TwelveData] Fundamentals error for {symbol}: {exc}")
                return {}
