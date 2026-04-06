from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.market import Market, Exchange, Interval

class SearchQuery(BaseModel):
    query: str
    market: Optional[Market] = None
    exchange: Optional[Exchange] = None
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
    chart: Optional[List[dict]] = None
    fundamentals: Optional[dict] = None
    depth: Optional[dict] = None
    processing_time_ms: float