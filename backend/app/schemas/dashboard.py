from pydantic import BaseModel


class DashboardSearchRequest(BaseModel):
    query: str


class DashboardSearchResponse(BaseModel):
    symbol: str
    query: str
    stock_data: dict
    news: dict
