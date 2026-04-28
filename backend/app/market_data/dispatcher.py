"""
app/market_data/dispatcher.py

Single entry point for all market data needs.
Automatically routes to the correct provider based on market/symbol.
Your existing API routes call ONLY this — they never touch providers directly.

Provider priority for US market:
1. TwelveData (primary with key rotation)
2. AlphaVantage (fallback)
3. Finnhub (fallback)

Provider for Indian market:
- Upstox (primary with key rotation)
"""

import logging
import re

from app.market_data.providers.twelve_data import TwelveDataProvider
from app.market_data.providers.upstox import UpstoxProvider
from app.schemas.market import Market, MarketDepth, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)

# Indian exchange symbols — NSE listed, ends with .NS in some systems
_INDIAN_SYMBOL_RE = re.compile(
    r"\.(NS|BO)$",  # Yahoo-style suffix
    re.IGNORECASE,
)

# Known Indian indices / exchange prefixes
_INDIAN_EXCHANGES = {"NSE", "BSE", "NSE_EQ", "BSE_EQ"}


def detect_market(symbol: str, exchange: str | None = None) -> Market:
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

    def __init__(
        self,
        alpha_vantage_provider=None,
        finnhub_provider=None,
        twelve_data_provider=None,
        upstox_provider=None,
    ):
        """
        Initialize dispatcher with optional fallback providers.

        Args:
            alpha_vantage_provider: AlphaVantageProvider instance (fallback for US)
            finnhub_provider: FinnhubProvider instance (fallback for US)
            twelve_data_provider: TwelveDataProvider instance (primary provider)
            upstox_provider: UpstoxProvider instance (fallback for India)
        """
        self.twelve_data = twelve_data_provider or TwelveDataProvider()
        self.upstox = upstox_provider or UpstoxProvider()
        self.alpha_vantage = alpha_vantage_provider
        self.finnhub = finnhub_provider

    # Quote

    async def get_quote(
        self,
        symbol: str,
        market: Market | None = None,
        exchange: str = "NSE_EQ",
    ) -> StockQuote | None:
        resolved = market or detect_market(symbol, exchange)

        # Try TwelveData first for all markets (primary provider)
        quote = await self.twelve_data.get_quote(symbol, exchange)
        if quote:
            return quote

        logger.warning(f"[Dispatcher] TwelveData failed for {symbol}, trying fallbacks")

        # India market fallback: Upstox
        if resolved == Market.INDIA:
            quote = await self.upstox.get_quote(symbol, exchange)
            if quote:
                logger.info(f"[Dispatcher] Upstox succeeded for {symbol}")
                return quote

        # US market fallbacks
        # Try AlphaVantage
        if self.alpha_vantage:
            quote = await self.alpha_vantage.get_quote(symbol)
            if quote:
                logger.info(f"[Dispatcher] AlphaVantage succeeded for {symbol}")
                return quote

        # Try Finnhub
        if self.finnhub:
            quote = await self.finnhub.get_quote(symbol)
            if quote:
                logger.info(f"[Dispatcher] Finnhub succeeded for {symbol}")
                return quote

        logger.error(f"[Dispatcher] All providers failed for {symbol}")
        return None

    # OHLCV Chart

    async def get_chart(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
        market: Market | None = None,
        exchange: str = "NSE_EQ",
        from_date: str = "",
        to_date: str = "",
    ) -> list[OHLCVPoint]:
        resolved = market or detect_market(symbol, exchange)

        # Try TwelveData first for all markets (primary provider)
        chart = await self.twelve_data.get_time_series(symbol, interval, outputsize, exchange)
        if chart:
            return chart

        logger.warning(f"[Dispatcher] TwelveData chart failed for {symbol}, trying fallbacks")

        # India market fallback: Upstox
        if resolved == Market.INDIA:
            upstox_interval = _map_interval_upstox(interval)
            chart = await self.upstox.get_historical(symbol, upstox_interval, exchange, from_date, to_date)
            if chart:
                logger.info(f"[Dispatcher] Upstox chart succeeded for {symbol}")
                return chart

        # US market fallbacks
        # Try AlphaVantage
        if self.alpha_vantage:
            chart = await self.alpha_vantage.get_time_series(symbol, interval, outputsize)
            if chart:
                logger.info(f"[Dispatcher] AlphaVantage chart succeeded for {symbol}")
                return chart

        # Try Finnhub
        if self.finnhub:
            chart = await self.finnhub.get_time_series(symbol, interval, outputsize)
            if chart:
                logger.info(f"[Dispatcher] Finnhub chart succeeded for {symbol}")
                return chart

        logger.error(f"[Dispatcher] All providers failed for chart {symbol}")
        return []

    # Market Depth  (India only)

    async def get_market_depth(
        self,
        symbol: str,
        exchange: str = "NSE_EQ",
    ) -> MarketDepth | None:
        return await self.upstox.get_market_depth(symbol, exchange)

    # Fundamentals

    async def get_fundamentals(
        self,
        symbol: str,
        market: Market | None = None,
    ) -> dict:
        resolved = market or detect_market(symbol)

        if resolved == Market.US:
            return await self.twelve_data.get_fundamentals(symbol)

        # Indian fundamentals: return empty dict for now
        # Wire to your existing app/api/financial.py when ready
        logger.info(f"[Dispatcher] Indian fundamentals for {symbol} — delegate to financial.py")
        return {}

    # Batch quotes  (for watchlist pages)

    async def get_batch_quotes(
        self,
        symbols: list[str],
        market: Market | None = None,
        exchange: str = "NSE_EQ",
    ) -> list[StockQuote | None]:
        """Fetch multiple quotes concurrently."""
        import asyncio

        tasks = [self.get_quote(s, market, exchange) for s in symbols]
        return list(await asyncio.gather(*tasks))


# Interval mapping helper

_INTERVAL_MAP: dict = {
    "1min": "1minute",
    "5min": "5minute",
    "15min": "30minute",
    "30min": "30minute",
    "1h": "1hour",
    "1hour": "1hour",
    "1day": "1day",
    "1week": "1week",
}


def _map_interval_upstox(interval: str) -> str:
    return _INTERVAL_MAP.get(interval.lower(), "1minute")
