from app.ingestion.financial_loader import FinancialLoader
from app.schemas.financial import FinancialResponse
from app.services.financial_metrics import calculate_top_metrics, clean_rate_limit
from app.services.stock_price_service import StockPriceService


class DataService:
    def __init__(self, financial_loader: FinancialLoader, stock_price_service: StockPriceService | None = None):
        self._financial_loader = financial_loader
        self._stock_price_service = stock_price_service

    async def get_financial_data(self, symbol: str):
        financials = await self._financial_loader.load_financials(symbol)

        # rate-limit
        financials["income_statement"] = clean_rate_limit(financials.get("income_statement"))
        financials["balance_sheet"] = clean_rate_limit(financials.get("balance_sheet"))
        financials["cash_flow"] = clean_rate_limit(financials.get("cash_flow"))

        # TOP 10
        metrics = calculate_top_metrics(financials)

        return FinancialResponse(symbol=symbol, financials=financials, metrics=metrics)

    async def get_stock_price(self, symbol: str):
        """Get current stock price to show in watchlist items"""
        # Use multi-provider service if available
        if self._stock_price_service:
            price = await self._stock_price_service.get_current_price(symbol)
            return {"symbol": symbol, "price": price}

        # Fallback to direct loader call
        stock_data = await self._financial_loader.load_stock_prices(symbol)

        if not stock_data or "Time Series (Daily)" not in stock_data:
            return {"symbol": symbol, "price": None}

        time_series = stock_data["Time Series (Daily)"]

        if time_series:
            latest_date = max(time_series.keys())
            latest_data = time_series[latest_date]
            price = float(latest_data.get("4. close", 0))
            return {"symbol": symbol, "price": price}

        return {"symbol": symbol, "price": None}
