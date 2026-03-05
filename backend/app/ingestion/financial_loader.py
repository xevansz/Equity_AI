"""Financial Data Loader"""

from app.mcp.financial_api import AlphaVantageMCP


class FinancialLoader:
    def __init__(self, alpha_vantage: AlphaVantageMCP):
        self._alpha_vantage = alpha_vantage

    async def load_financials(self, symbol: str):
        income = await self._alpha_vantage.get_income_statement(symbol)
        balance = await self._alpha_vantage.get_balance_sheet(symbol)
        cash_flow = await self._alpha_vantage.get_cash_flow(symbol)

        return {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow,
        }


financial_loader = FinancialLoader(AlphaVantageMCP())
