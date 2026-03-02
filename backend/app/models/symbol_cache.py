from datetime import datetime

from pydantic import BaseModel, Field


class SymbolCache(BaseModel):
    company_name: str
    symbol: str
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    created_at: datetime
    last_used: datetime
    use_count: int = 1
