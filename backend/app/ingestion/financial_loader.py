"""Financial Data Loader"""

from typing import Any

from app.logging_config import get_logger
from app.mcp.financial_api import AlphaVantageMCP

logger = get_logger(__name__)


class FinancialLoader:
    """Loader for financial data from various sources."""

    def __init__(self, alpha_vantage: AlphaVantageMCP, stock_price_service: Any | None = None) -> None:
        """Initialize financial loader.

        Args:
            alpha_vantage: Alpha Vantage API client
            stock_price_service: Optional multi-provider stock price service (MarketDataDispatcher)
        """
        self._alpha_vantage = alpha_vantage
        self._stock_price_service = stock_price_service

    async def load_financials(self, symbol: str) -> dict[str, Any]:
        """Load financial statements for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing income statement, balance sheet, and cash flow
        """
        income = await self._alpha_vantage.get_income_statement(symbol)
        balance = await self._alpha_vantage.get_balance_sheet(symbol)
        cash_flow = await self._alpha_vantage.get_cash_flow(symbol)

        return {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow,
        }

    async def load_stock_prices(self, symbol: str) -> dict[str, Any]:
        """Load stock price time series for a symbol.

        Uses MarketDataDispatcher if available (multi-provider with fallback),
        otherwise falls back to direct AlphaVantage API.

        Args:
            symbol: Stock symbol

        Returns:
            Time series data dictionary in AlphaVantage format
        """
        if self._stock_price_service:
            try:
                # Use MarketDataDispatcher for multi-provider fallback
                chart_data = await self._stock_price_service.get_chart(symbol, interval="1day", outputsize=100)

                if not chart_data:
                    logger.warning(f"MarketDataDispatcher returned no data for {symbol}, trying AlphaVantage")
                    return await self._alpha_vantage.get_time_series_daily(symbol)

                # Convert OHLCVPoint list to AlphaVantage format for backward compatibility
                time_series = {}
                for point in chart_data:
                    time_series[point.timestamp] = {
                        "1. open": str(point.open),
                        "2. high": str(point.high),
                        "3. low": str(point.low),
                        "4. close": str(point.close),
                        "5. volume": str(point.volume),
                    }

                return {"Time Series (Daily)": time_series}

            except Exception as e:
                logger.error(f"Error using MarketDataDispatcher for {symbol}: {e}, falling back to AlphaVantage")
                return await self._alpha_vantage.get_time_series_daily(symbol)

        return await self._alpha_vantage.get_time_series_daily(symbol)
