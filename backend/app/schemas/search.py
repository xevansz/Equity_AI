
from pydantic import BaseModel, Field

from app.schemas.market import Exchange, Interval, Market


class SearchQuery(BaseModel):
    query: str
    market: Market | None = None
    exchange: Exchange | None = None
    interval: Interval = Interval.FIVE_MIN
    chart_size: int = Field(100, ge=10, le=500)
    include_depth: bool = True
    include_fundamentals: bool = True
    include_chart: bool = True

class UnifiedSearchResponse(BaseModel):
    symbol: str
    market: Market
    exchange: Exchange
    market_status: dict
    quote: dict
    chart: list[dict] | None = None
    fundamentals: dict | None = None
    depth: dict | None = None
    processing_time_ms: float