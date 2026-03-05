"""Health Check Schema"""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    db_status: str
    llm_status: str
    timestamp: datetime
    service: str
