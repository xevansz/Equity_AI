"""
app/market_data/providers/alpha_vantage.py

AlphaVantage provider wrapper - fallback for US market data
"""

import logging

from app.mcp.financial_api import AlphaVantageMCP
from app.schemas.market import Market, OHLCVPoint, StockQuote

logger = logging.getLogger(__name__)


class AlphaVantageProvider:
    """
    Wrapper for AlphaVantage MCP to match the provider interface.
    Used as fallback when TwelveData fails.
    """

    def __init__(self, client: AlphaVantageMCP):
        self.client = client

    async def get_quote(self, symbol: str) -> StockQuote | None:
        """Fetch quote from AlphaVantage TIME_SERIES_DAILY endpoint"""
        try:
            data = await self.client.get_time_series_daily(symbol)
            
            if not data or "Time Series (Daily)" not in data:
                logger.warning(f"[AlphaVantage] No time series data for {symbol}")
                return None
            
            time_series = data["Time Series (Daily)"]
            if not time_series:
                return None
            
            # Get the latest date
            latest_date = max(time_series.keys())
            latest = time_series[latest_date]
            
            # Get previous date for change calculation
            dates = sorted(time_series.keys(), reverse=True)
            prev_close = float(latest.get("4. close", 0))
            if len(dates) > 1:
                prev_close = float(time_series[dates[1]].get("4. close", prev_close))
            
            current_price = float(latest.get("4. close", 0))
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0
            
            return StockQuote(
                symbol=symbol.upper(),
                price=current_price,
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=int(latest.get("5. volume", 0)),
                high=float(latest.get("2. high", 0)),
                low=float(latest.get("3. low", 0)),
                open=float(latest.get("1. open", 0)),
                prev_close=prev_close,
                timestamp=latest_date,
                market=Market.US,
            )
        except Exception as exc:
            logger.exception(f"[AlphaVantage] Quote error for {symbol}: {exc}")
            return None

    async def get_time_series(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: int = 100,
    ) -> list[OHLCVPoint]:
        """Fetch time series data from AlphaVantage"""
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
            logger.exception(f"[AlphaVantage] Time series error for {symbol}: {exc}")
            return []
