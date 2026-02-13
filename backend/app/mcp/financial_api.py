"""Financial Data APIs"""

from mcp.base import BaseMCP
from config import settings


class AlphaVantageMCP(BaseMCP):
    def __init__(self):
        super().__init__(
            "https://www.alphavantage.co/query", settings.ALPHA_VANTAGE_API_KEY
        )

    async def get_income_statement(self, symbol: str):
        return await self.get("", {"function": "INCOME_STATEMENT", "symbol": symbol})

    async def get_balance_sheet(self, symbol: str):
        return await self.get("", {"function": "BALANCE_SHEET", "symbol": symbol})

    async def get_cash_flow(self, symbol: str):
        return await self.get("", {"function": "CASH_FLOW", "symbol": symbol})


alpha_vantage = AlphaVantageMCP()
