from datetime import datetime

from pydantic import BaseModel


class Symbol(BaseModel):
    symbol: str
    canonical_name: str
    created_at: datetime


class SymbolAlias(BaseModel):
    symbol: str
    alias_name: str
    normalized_alias: str
    created_at: datetime
    last_used: datetime
    use_count: int = 0
