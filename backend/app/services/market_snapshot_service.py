"""Market snapshot extraction service"""

from datetime import datetime, time

from app.logging_config import get_logger
from app.schemas.dashboard import MarketSnapshot

logger = get_logger(__name__)


def extract_market_snapshot(stock_data: dict, symbol: str) -> MarketSnapshot | None:
    """
    Extract market snapshot from Alpha Vantage time series data.

    Args:
        stock_data: Time series data from Alpha Vantage
        symbol: Stock symbol

    Returns:
        MarketSnapshot with current market metrics or None if data unavailable
    """
    if not stock_data or "Time Series (Daily)" not in stock_data:
        logger.warning("No time series data available for %s", symbol)
        return None

    time_series = stock_data["Time Series (Daily)"]
    if not time_series:
        logger.warning("Empty time series for %s", symbol)
        return None

    try:
        sorted_dates = sorted(time_series.keys(), reverse=True)
        latest_date = sorted_dates[0]
        latest_data = time_series[latest_date]

        price = float(latest_data.get("4. close", 0))
        open_price = float(latest_data.get("1. open", 0))
        high = float(latest_data.get("2. high", 0))
        low = float(latest_data.get("3. low", 0))
        volume = int(float(latest_data.get("5. volume", 0)))

        prev_close = None
        if len(sorted_dates) > 1:
            prev_date = sorted_dates[1]
            prev_data = time_series[prev_date]
            prev_close = float(prev_data.get("4. close", 0))

        change = None
        change_percent = None
        if prev_close and prev_close > 0:
            change = price - prev_close
            change_percent = (change / prev_close) * 100

        market = _infer_market(symbol)
        status = _determine_market_status(market, latest_date)

        return MarketSnapshot(
            price=price,
            change=change,
            change_percent=change_percent,
            volume=volume,
            high=high,
            low=low,
            open=open_price,
            prev_close=prev_close,
            timestamp=latest_date,
            market=market,
            status=status,
        )
    except (KeyError, ValueError, IndexError) as e:
        logger.error("Error extracting market snapshot for %s: %s", symbol, str(e))
        return None


def _infer_market(symbol: str) -> str:
    """
    Infer market from symbol.

    This is a simple heuristic. For more accuracy, you could query
    Alpha Vantage's SYMBOL_SEARCH or maintain a symbol->exchange mapping.
    """
    if "." in symbol:
        return symbol.split(".")[-1]

    return "US"


def _determine_market_status(market: str, timestamp: str | None) -> str | None:
    """
    Determine market status based on market and timestamp.

    For US markets, infers open/closed based on US Eastern Time trading hours.
    For non-US markets, returns None (no inference).

    Args:
        market: Market identifier (e.g., "US", "NSE", "LSE")
        timestamp: Latest data timestamp (YYYY-MM-DD format)

    Returns:
        "Open" or "Closed" for US markets, None for others
    """
    if market != "US":
        return None

    try:
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()

        market_open = time(9, 30)
        market_close = time(16, 0)

        if current_weekday >= 5:
            return "Closed"

        if market_open <= current_time <= market_close:
            return "Open"
        else:
            return "Closed"

    except Exception as e:
        logger.warning("Error determining market status: %s", str(e))
        return None
