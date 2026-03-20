from datetime import UTC, datetime

from pydantic import BaseModel, Field


class WatchlistItem(BaseModel):
    symbol: str
    name: str
    company_name: str
    user_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WatchlistCreate(BaseModel):
    symbol: str
    name: str
    company_name: str


class WatchlistItemOut(BaseModel):
    symbol: str
    name: str
    company_name: str
    added_at: datetime


class WatchlistListResponse(BaseModel):
    items: list[WatchlistItemOut]
    next_cursor: datetime | None
    limit: int
