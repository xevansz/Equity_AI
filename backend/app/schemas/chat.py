from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
