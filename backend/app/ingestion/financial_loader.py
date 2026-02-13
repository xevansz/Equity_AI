"""Financial Data Loader"""

from mcp.financial_api import alpha_vantage


class FinancialLoader:
    async def load_financials(self, symbol: str):
        income = await alpha_vantage.get_income_statement(symbol)
        balance = await alpha_vantage.get_balance_sheet(symbol)
        cash_flow = await alpha_vantage.get_cash_flow(symbol)

        return {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow,
        }


financial_loader = FinancialLoader()
