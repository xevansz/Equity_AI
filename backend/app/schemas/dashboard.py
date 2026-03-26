from pydantic import BaseModel


class DashboardSearchRequest(BaseModel):
    query: str


class MarketSnapshot(BaseModel):
    price: float | None = None
    change: float | None = None
    change_percent: float | None = None
    volume: int | None = None
    high: float | None = None
    low: float | None = None
    open: float | None = None
    prev_close: float | None = None
    timestamp: str | None = None
    market: str | None = None


class DashboardSearchResponse(BaseModel):
    symbol: str
    query: str
    company_name: str
    stock_data: dict
    news: dict
    market_snapshot: MarketSnapshot | None = None
