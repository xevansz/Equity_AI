from datetime import datetime

from pydantic import BaseModel


class SymbolCache(BaseModel):
    company_name: str
    symbol: str
    display_name: str
    aliases: list[str] = []
    created_at: datetime
    last_used: datetime
    use_count: int = 1
