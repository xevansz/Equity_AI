from app.ingestion.financial_loader import FinancialLoader
from app.market_data.dispatcher import MarketDataDispatcher
from app.schemas.financial import FinancialResponse
from app.services.financial_metrics import (
    calculate_top_metrics,
    clean_rate_limit,
)
from app.services.market_snapshot_service import (
    _determine_market_status,
    _infer_market,
)
from app.utils.market_resolver import resolve_market_from_symbol


class DataService:
    def __init__(
        self,
        financial_loader: FinancialLoader,
        market_dispatcher: MarketDataDispatcher | None = None,
    ):
        self._financial_loader = financial_loader
        self._market_dispatcher = market_dispatcher

    async def get_financial_data(self, symbol: str):
        financials = await self._financial_loader.load_financials(symbol)

        # rate-limit
        financials["income_statement"] = clean_rate_limit(financials.get("income_statement"))
        financials["balance_sheet"] = clean_rate_limit(financials.get("balance_sheet"))
        financials["cash_flow"] = clean_rate_limit(financials.get("cash_flow"))

        # Fetch current price for PE ratio calculation
        current_price = None
        if self._market_dispatcher:
            market, exchange, clean_symbol = resolve_market_from_symbol(symbol)
            quote = await self._market_dispatcher.get_quote(clean_symbol, market, exchange.value)
            if quote:
                current_price = quote.price

        financials["current_price"] = current_price

        # TOP 10
        metrics = calculate_top_metrics(financials)

        return FinancialResponse(symbol=symbol, financials=financials, metrics=metrics)

    async def get_stock_price(self, symbol: str):
        """
        Get current stock price - DEPRECATED: Use WebSocket /api/ws/stream instead

        This method is kept for backward compatibility but clients should migrate
        to WebSocket for real-time updates.
        """
        if self._market_dispatcher:
            # Use new MarketDataDispatcher
            market, exchange, clean_symbol = resolve_market_from_symbol(symbol)
            quote = await self._market_dispatcher.get_quote(clean_symbol, market, exchange.value)

            if quote:
                return {
                    "symbol": quote.symbol,
                    "price": quote.price,
                    "market": quote.market.value,
                    "status": "open",  # Could enhance with market_utils.get_market_status
                }

        # Fallback to old method if dispatcher not available
        market = _infer_market(symbol)
        stock_data = await self._financial_loader.load_stock_prices(symbol)

        if not stock_data or "Time Series (Daily)" not in stock_data:
            status = _determine_market_status(market, None)
            return {"symbol": symbol, "price": None, "market": market, "status": status}

        time_series = stock_data["Time Series (Daily)"]

        if time_series:
            latest_date = max(time_series.keys())
            latest_data = time_series[latest_date]
            price = float(latest_data.get("4. close", 0))
            status = _determine_market_status(market, latest_date)
            return {"symbol": symbol, "price": price, "market": market, "status": status}

        status = _determine_market_status(market, None)
        return {"symbol": symbol, "price": None, "market": market, "status": status}
