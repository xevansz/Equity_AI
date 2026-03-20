from pydantic import BaseModel


class DashboardSearchRequest(BaseModel):
    query: str


class DashboardSearchResponse(BaseModel):
    symbol: str
    query: str
    company_name: str
    stock_data: dict
    news: dict
