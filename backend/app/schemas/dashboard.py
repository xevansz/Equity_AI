from pydantic import BaseModel, Field, field_validator


class DashboardSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, description="Search query for company or symbol")
    market: str = Field(default="US", description="Market: US or INDIA")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


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
    status: str | None = None


class DashboardSearchResponse(BaseModel):
    symbol: str
    query: str
    company_name: str
    stock_data: dict
    intraday_data: list = []
    news: dict
    market_snapshot: MarketSnapshot | None = None
    search_status: str = "ok"
    message: str | None = None
