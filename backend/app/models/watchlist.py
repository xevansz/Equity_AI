from datetime import UTC, datetime

from pydantic import BaseModel, Field


class WatchlistItem(BaseModel):
    symbol: str
    name: str
    user_id: str
    added_at: datetime = Field(default_factory=datetime.now(UTC))


class WatchlistCreate(BaseModel):
    symbol: str
    name: str
