"""Watchlist API Schemas"""

from pydantic import BaseModel


class WatchlistCreate(BaseModel):
    symbol: str
    name: str
