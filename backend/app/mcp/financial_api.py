"""Financial Data APIs"""

from app.config import settings
from app.mcp.base import BaseMCP


class AlphaVantageMCP(BaseMCP):
    CACHE_TTL: float = 300.0  # 5 min — matches Alpha Vantage free-tier rate limit

    def __init__(self):
        super().__init__("https://www.alphavantage.co/query", settings.ALPHA_VANTAGE_API_KEY)

    async def get_income_statement(self, symbol: str):
        return await self.get("", {"function": "INCOME_STATEMENT", "symbol": symbol})

    async def get_balance_sheet(self, symbol: str):
        return await self.get("", {"function": "BALANCE_SHEET", "symbol": symbol})

    async def get_cash_flow(self, symbol: str):
        return await self.get("", {"function": "CASH_FLOW", "symbol": symbol})

    async def get_time_series_daily(self, symbol: str):
        return await self.get("", {"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "compact"})
