from app.ingestion.financial_loader import financial_loader
from app.schemas.financial import FinancialResponse
from app.services.financial_metrics import calculate_top_metrics, clean_rate_limit


class DataService:
    async def get_financial_data(self, symbol: str):
        financials = await financial_loader.load_financials(symbol)

        # --- Clean Alpha Vantage rate-limit responses ---
        financials["income_statement"] = clean_rate_limit(
            financials.get("income_statement")
        )
        financials["balance_sheet"] = clean_rate_limit(financials.get("balance_sheet"))
        financials["cash_flow"] = clean_rate_limit(financials.get("cash_flow"))

        # --- Calculate TOP 10 METRICS ---
        metrics = calculate_top_metrics(financials)

        return FinancialResponse(symbol=symbol, financials=financials, metrics=metrics)
