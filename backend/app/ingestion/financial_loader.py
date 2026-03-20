"""Financial Data Loader"""

from app.mcp.financial_api import AlphaVantageMCP
from app.services.stock_price_service import StockPriceService


class FinancialLoader:
    def __init__(self, alpha_vantage: AlphaVantageMCP, stock_price_service: StockPriceService | None = None):
        self._alpha_vantage = alpha_vantage
        self._stock_price_service = stock_price_service

    async def load_financials(self, symbol: str):
        income = await self._alpha_vantage.get_income_statement(symbol)
        balance = await self._alpha_vantage.get_balance_sheet(symbol)
        cash_flow = await self._alpha_vantage.get_cash_flow(symbol)

        return {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow,
        }

    async def load_stock_prices(self, symbol: str):
        # Use multi-provider service if available, otherwise fallback to Alpha Vantage
        if self._stock_price_service:
            return await self._stock_price_service.get_time_series_daily(symbol)
        return await self._alpha_vantage.get_time_series_daily(symbol)
