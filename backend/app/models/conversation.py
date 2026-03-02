"""Conversation Model"""

from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    session_id: str
    role: str
    content: str
    timestamp: datetime


class SearchRequest(BaseModel):
    query: str
    symbol: str | None = None
