"""Multi-provider stock price service with automatic fallback"""

import asyncio

from app.logging_config import get_logger
from app.mcp.financial_api import AlphaVantageMCP
from app.mcp.finnhub_api import FinnhubMCP

logger = get_logger(__name__)


class StockPriceService:
    """Manages multiple stock data providers with automatic fallback"""

    def __init__(
        self,
        alpha_vantage: AlphaVantageMCP,
        finnhub: FinnhubMCP | None = None,
    ):
        self.providers = []

        if alpha_vantage:
            self.providers.append(("AlphaVantage", alpha_vantage))
        if finnhub:
            self.providers.append(("Finnhub", finnhub))

        self.current_provider_index = 0
        self._in_flight: dict[str, asyncio.Task] = {}

    async def get_time_series_daily(self, symbol: str) -> dict:
        """Get daily time series data with automatic provider fallback"""
        # Check if there's already an in-flight request for this symbol
        if symbol in self._in_flight:
            logger.debug("Reusing in-flight request for %s", symbol)
            return await self._in_flight[symbol]

        # Create new task and store it
        task = asyncio.create_task(self._fetch_time_series(symbol))
        self._in_flight[symbol] = task

        try:
            return await task
        finally:
            # Clean up completed task
            self._in_flight.pop(symbol, None)

    async def _fetch_time_series(self, symbol: str) -> dict:
        """Internal method to fetch time series data"""
        if not self.providers:
            logger.error("No stock data providers configured")
            return {}

        # Try each provider in order
        for _ in range(len(self.providers)):
            provider_name, provider = self.providers[self.current_provider_index]

            try:
                logger.debug("Fetching time series for %s from %s", symbol, provider_name)
                data = await provider.get_time_series_daily(symbol)

                # Check if we got valid data
                if data and "Time Series (Daily)" in data and data["Time Series (Daily)"]:
                    logger.info("Successfully fetched data from %s", provider_name)
                    return data

                # Check for rate limit response from Alpha Vantage
                if "Note" in data or "Information" in data:
                    logger.warning("%s rate limited: %s", provider_name, data.get("Note") or data.get("Information"))
                    self._rotate_provider()
                    continue

                logger.warning("%s returned empty data for %s", provider_name, symbol)

            except Exception as e:
                logger.warning("Error fetching from %s: %s", provider_name, str(e))
                self._rotate_provider()
                continue

        logger.error("All providers failed for symbol: %s", symbol)
        return {}

    async def get_current_price(self, symbol: str) -> float | None:
        """Get current stock price with automatic provider fallback"""
        if not self.providers:
            return None

        # Try time series first
        data = await self.get_time_series_daily(symbol)

        if data and "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            if time_series:
                latest_date = max(time_series.keys())
                latest_data = time_series[latest_date]
                return float(latest_data.get("4. close", 0))

        return None

    def _rotate_provider(self):
        """Rotate to the next provider"""
        self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        provider_name = self.providers[self.current_provider_index][0]
        logger.info("Rotated to provider: %s", provider_name)
