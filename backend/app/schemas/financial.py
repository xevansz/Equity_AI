"""Financial Schemas"""

from pydantic import BaseModel


class FinancialRequest(BaseModel):
    symbol: str


class FinancialResponse(BaseModel):
    symbol: str
    financials: dict
    metrics: dict
