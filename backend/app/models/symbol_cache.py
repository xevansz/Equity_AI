from pydantic import BaseModel
from datetime import datetime
from typing import List


class SymbolCache(BaseModel):
  company_name: str
  symbol: str
  display_name: str
  aliases: List[str] = []
  created_at: datetime
  last_used: datetime
  use_count: int = 1
