from app.ingestion.financial_loader import FinancialLoader
from app.schemas.financial import FinancialResponse
from app.services.financial_metrics import calculate_top_metrics, clean_rate_limit


class DataService:
    def __init__(self, financial_loader: FinancialLoader):
        self._financial_loader = financial_loader

    async def get_financial_data(self, symbol: str):
        financials = await self._financial_loader.load_financials(symbol)

        # rate-limit
        financials["income_statement"] = clean_rate_limit(financials.get("income_statement"))
        financials["balance_sheet"] = clean_rate_limit(financials.get("balance_sheet"))
        financials["cash_flow"] = clean_rate_limit(financials.get("cash_flow"))

        # TOP 10
        metrics = calculate_top_metrics(financials)

        return FinancialResponse(symbol=symbol, financials=financials, metrics=metrics)
