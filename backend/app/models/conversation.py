"""Conversation Model"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Message(BaseModel):
    session_id: str
    role: str
    content: str
    timestamp: datetime


class SearchRequest(BaseModel):
    query: str
    symbol: Optional[str] = None
