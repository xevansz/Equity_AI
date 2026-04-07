"""
app/market_data/providers/finnhub.py

Finnhub provider wrapper - fallback for US market data
"""

import logging

from app.mcp.finnhub_api import FinnhubMCP
from app.schemas.market import Market, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)


class FinnhubProvider:
    """
    Wrapper for Finnhub MCP to match the provider interface.
    Used as fallback when TwelveData and AlphaVantage fail.
    """

    def __init__(self, client: FinnhubMCP):
        self.client = client

    async def get_quote(self, symbol: str) -> StockQuote | None:
        """Fetch quote from Finnhub"""
        try:
            data = await self.client.get_quote(symbol)
            
            if not data or "c" not in data:
                logger.warning(f"[Finnhub] No quote data for {symbol}")
                return None
            
            current_price = float(data.get("c", 0))
            prev_close = float(data.get("pc", current_price))
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0
            
            return StockQuote(
                symbol=symbol.upper(),
                price=current_price,
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=0,  # Finnhub quote doesn't include volume
                high=float(data.get("h", 0)),
                low=float(data.get("l", 0)),
                open=float(data.get("o", 0)),
                prev_close=prev_close,
                timestamp=str(data.get("t", "")),
                market=Market.US,
            )
        except Exception as exc:
            logger.exception(f"[Finnhub] Quote error for {symbol}: {exc}")
            return None

    async def get_time_series(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
    ) -> list[OHLCVPoint]:
        """Fetch time series data from Finnhub"""
        try:
            data = await self.client.get_time_series_daily(symbol)
            
            if not data or "Time Series (Daily)" not in data:
                return []
            
            time_series = data["Time Series (Daily)"]
            
            # Convert to OHLCVPoint list
            points = []
            for date in sorted(time_series.keys(), reverse=True)[:outputsize]:
                day_data = time_series[date]
                points.append(
                    OHLCVPoint(
                        timestamp=date,
                        open=float(day_data.get("1. open", 0)),
                        high=float(day_data.get("2. high", 0)),
                        low=float(day_data.get("3. low", 0)),
                        close=float(day_data.get("4. close", 0)),
                        volume=int(day_data.get("5. volume", 0)),
                    )
                )
            
            return points
        except Exception as exc:
            logger.exception(f"[Finnhub] Time series error for {symbol}: {exc}")
            return []
