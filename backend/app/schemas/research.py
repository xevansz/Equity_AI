"""Research Schemas"""

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    symbol: str


class ResearchResponse(BaseModel):
    symbol: str
    Data_CoT: str
    Thesis_CoT: str
    Valuation: str
    Risk_CoT: str
