"""Financial Data Models"""

from pydantic import BaseModel


class FinancialStatement(BaseModel):
    symbol: str
    period: str
    revenue: float
    net_income: float
    assets: float
    liabilities: float
