"""Research Schemas"""

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    symbol: str


class ResearchResponse(BaseModel):
    symbol: str
    report: str
    analysis: dict
