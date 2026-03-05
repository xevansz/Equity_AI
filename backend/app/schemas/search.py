"""Search Schemas"""

from pydantic import BaseModel

from app.schemas.chat import ChatResponse
from app.schemas.financial import FinancialResponse


class SearchRequest(BaseModel):
    query: str
    symbol: str | None = None


class SearchResponse(BaseModel):
    query: str
    symbol: str
    chat: ChatResponse
    financial: FinancialResponse | None
    research: dict
    news: dict
