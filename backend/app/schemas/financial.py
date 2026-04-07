"""Financial Schemas"""

import re

from pydantic import BaseModel, Field, field_validator


class FinancialRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty or whitespace only")
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9.\-:]+$", v):
            raise ValueError("Symbol must contain only alphanumeric characters, dots, hyphens, or colons")
        return v


class FinancialResponse(BaseModel):
    symbol: str
    financials: dict
    metrics: dict
