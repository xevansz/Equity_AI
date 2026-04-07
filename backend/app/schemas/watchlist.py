"""Watchlist API Schemas"""

import re

from pydantic import BaseModel, Field, field_validator


class WatchlistCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol")
    name: str = Field(..., min_length=1, max_length=200, description="Display name")
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty or whitespace only")
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9.\-:]+$", v):
            raise ValueError("Symbol must contain only alphanumeric characters, dots, hyphens, or colons")
        return v

    @field_validator("name", "company_name")
    @classmethod
    def validate_text_fields(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()
