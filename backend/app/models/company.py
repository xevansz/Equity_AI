"""Company Model"""

from pydantic import BaseModel


class Company(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str
