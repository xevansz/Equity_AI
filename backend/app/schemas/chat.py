from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000, description="User query")
    session_id: str = Field(default="default", min_length=1, max_length=100, description="Session ID")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty or whitespace only")
        return v.strip()


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
