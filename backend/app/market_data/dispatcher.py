"""
app/market_data/dispatcher.py

Single entry point for all market data needs.
Automatically routes to the correct provider based on market/symbol.
Your existing API routes call ONLY this — they never touch providers directly.
"""

import logging
import re
from typing import List, Optional

from app.market_data.providers.twelve_data import TwelveDataProvider
from app.market_data.providers.upstox import UpstoxProvider
from app.schemas.market import Market, MarketDepth, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)

# Indian exchange symbols — NSE listed, ends with .NS in some systems
_INDIAN_SYMBOL_RE = re.compile(
    r"\.(NS|BO)$",          # Yahoo-style suffix
    re.IGNORECASE,
)

# Known Indian indices / exchange prefixes
_INDIAN_EXCHANGES = {"NSE", "BSE", "NSE_EQ", "BSE_EQ"}


def detect_market(symbol: str, exchange: Optional[str] = None) -> Market:
    """
    Detect market from symbol / exchange hint.
    Priority: explicit exchange > suffix > default US
    """
    if exchange and exchange.upper() in _INDIAN_EXCHANGES:
        return Market.INDIA
    if _INDIAN_SYMBOL_RE.search(symbol):
        return Market.INDIA
    return Market.US


class MarketDataDispatcher:
    """
    Unified interface — one class, all markets.

    All public methods accept an optional `market` parameter.
    If omitted, market is auto-detected from the symbol.

    Example:
        dispatcher = MarketDataDispatcher()
        quote = await dispatcher.get_quote("AAPL")
        quote = await dispatcher.get_quote("HINDCOPPER", market=Market.INDIA)
        candles = await dispatcher.get_chart("AAPL", interval="5min")
    """

    # ------------------------------------------------------------------
    # Quote
    # ------------------------------------------------------------------

    async def get_quote(
        self,
        symbol: str,
        market: Optional[Market] = None,
        exchange: str = "NSE_EQ",
    ) -> Optional[StockQuote]:
        resolved = market or detect_market(symbol, exchange)

        if resolved == Market.INDIA:
            return await UpstoxProvider.get_quote(symbol, exchange)
        return await TwelveDataProvider.get_quote(symbol)

    # ------------------------------------------------------------------
    # OHLCV Chart
    # ------------------------------------------------------------------

    async def get_chart(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
        market: Optional[Market] = None,
        exchange: str = "NSE_EQ",
        from_date: str = "",
        to_date: str = "",
    ) -> List[OHLCVPoint]:
        resolved = market or detect_market(symbol, exchange)

        if resolved == Market.INDIA:
            # Map generic intervals to Upstox format
            upstox_interval = _map_interval_upstox(interval)
            return await UpstoxProvider.get_historical(
                symbol, upstox_interval, exchange, from_date, to_date
            )

        return await TwelveDataProvider.get_time_series(symbol, interval, outputsize)

    # ------------------------------------------------------------------
    # Market Depth  (India only)
    # ------------------------------------------------------------------

    async def get_market_depth(
        self,
        symbol: str,
        exchange: str = "NSE_EQ",
    ) -> Optional[MarketDepth]:
        return await UpstoxProvider.get_market_depth(symbol, exchange)

    # ------------------------------------------------------------------
    # Fundamentals
    # ------------------------------------------------------------------

    async def get_fundamentals(
        self,
        symbol: str,
        market: Optional[Market] = None,
    ) -> dict:
        resolved = market or detect_market(symbol)

        if resolved == Market.US:
            return await TwelveDataProvider.get_fundamentals(symbol)

        # Indian fundamentals: return empty dict for now
        # Wire to your existing app/api/financial.py when ready
        logger.info(f"[Dispatcher] Indian fundamentals for {symbol} — delegate to financial.py")
        return {}

    # ------------------------------------------------------------------
    # Batch quotes  (for watchlist pages)
    # ------------------------------------------------------------------

    async def get_batch_quotes(
        self,
        symbols: List[str],
        market: Optional[Market] = None,
        exchange: str = "NSE_EQ",
    ) -> List[Optional[StockQuote]]:
        """Fetch multiple quotes concurrently."""
        import asyncio

        tasks = [self.get_quote(s, market, exchange) for s in symbols]
        return list(await asyncio.gather(*tasks))


# ------------------------------------------------------------------
# Interval mapping helper
# ------------------------------------------------------------------

_INTERVAL_MAP: dict = {
    "1min":  "1minute",
    "5min":  "5minute",
    "15min": "30minute",
    "30min": "30minute",
    "1h":    "1hour",
    "1hour": "1hour",
    "1day":  "1day",
    "1week": "1week",
}


def _map_interval_upstox(interval: str) -> str:
    return _INTERVAL_MAP.get(interval.lower(), "1minute")
