from enum import StrEnum

from pydantic import BaseModel


class Market(StrEnum):
    US = "US"
    INDIA = "INDIA"


class Exchange(StrEnum):
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    NSE = "NSE"
    NSE_EQ = "NSE_EQ"
    BSE = "BSE"
    BSE_EQ = "BSE_EQ"


class Interval(StrEnum):
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    ONE_HOUR = "1h"
    ONE_DAY = "1day"
    ONE_WEEK = "1week"
    ONE_MONTH = "1month"


class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    prev_close: float
    timestamp: str
    market: Market


class OHLCVPoint(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class MarketDepth(BaseModel):
    symbol: str
    buy_orders: list[dict]
    sell_orders: list[dict]
    buy_percentage: float
    sell_percentage: float
