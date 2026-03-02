"""Chat Schemas"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: list = []
