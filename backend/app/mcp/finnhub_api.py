"""Finnhub Stock Data API"""

from datetime import datetime, timedelta

from app.mcp.base import BaseMCP


class FinnhubMCP(BaseMCP):
    CACHE_TTL: float = 300.0  # 5 min

    def __init__(self, api_key: str):
        super().__init__("https://finnhub.io/api/v1", api_key)

    async def get_time_series_daily(self, symbol: str):
        """Get daily stock prices for the last 30 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        params = {
            "symbol": symbol,
            "resolution": "D",
            "from": int(start_date.timestamp()),
            "to": int(end_date.timestamp()),
            "token": self.api_key,
        }

        response = await self.get("/stock/candle", params)

        # Convert Finnhub format to Alpha Vantage format for compatibility
        if response.get("s") == "ok" and "t" in response:
            time_series = {}
            for i in range(len(response["t"])):
                date = datetime.fromtimestamp(response["t"][i]).strftime("%Y-%m-%d")
                time_series[date] = {
                    "1. open": str(response["o"][i]),
                    "2. high": str(response["h"][i]),
                    "3. low": str(response["l"][i]),
                    "4. close": str(response["c"][i]),
                    "5. volume": str(response["v"][i]),
                }

            return {"Time Series (Daily)": time_series}

        return {}

    async def get_quote(self, symbol: str):
        """Get current stock quote"""
        params = {"symbol": symbol, "token": self.api_key}
        return await self.get("/quote", params)
