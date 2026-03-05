"""Conversation DB Document Model"""

from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    session_id: str
    role: str
    content: str
    timestamp: datetime
