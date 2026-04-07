from pydantic import BaseModel, Field, field_validator

from app.schemas.market import Exchange, Interval, Market


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=50, description="Stock symbol or query")
    market: Market | None = None
    exchange: Exchange | None = None
    interval: Interval = Interval.FIVE_MIN
    chart_size: int = Field(100, ge=10, le=500)
    include_depth: bool = True
    include_fundamentals: bool = True
    include_chart: bool = True

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class BatchSearchRequest(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=50, description="List of stock symbols or queries")

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Queries list cannot be empty")
        if len(v) > 50:
            raise ValueError("Maximum 50 queries allowed per batch")
        validated = []
        for query in v:
            if not query or not query.strip():
                raise ValueError("Each query must be non-empty")
            validated.append(query.strip())
        return validated


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
