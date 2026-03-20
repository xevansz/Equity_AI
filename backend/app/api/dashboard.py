"""Dashboard API Endpoint"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import (
    get_current_user,
    get_database,
    get_financial_loader,
    get_news_loader,
)
from app.ingestion.financial_loader import FinancialLoader
from app.ingestion.news_loader import NewsLoader
from app.llm.symbol_resolver import symbol_resolver
from app.logging_config import get_logger
from app.schemas.dashboard import DashboardSearchRequest, DashboardSearchResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.post("/search", response_model=DashboardSearchResponse)
async def dashboard_search(
    request: DashboardSearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    financial_loader: FinancialLoader = Depends(get_financial_loader),
    news_loader: NewsLoader = Depends(get_news_loader),
) -> DashboardSearchResponse:
    """Dashboard search - returns only stock price data and news (no LLM)"""
    query = request.query

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    symbol, company_name = await symbol_resolver(query, db)

    logger.info("Dashboard search called (query=%s symbol=%s)", query, symbol)

    try:
        stock_data_task = financial_loader.load_stock_prices(symbol)
        news_task = news_loader.load_news(symbol, company_name, db=db)

        stock_data, news_docs = await asyncio.gather(
            stock_data_task,
            news_task,
        )

        logger.info("News articles fetched: %s", len(news_docs) if news_docs else 0)
        logger.debug("Stock data keys: %s", list(stock_data.keys()) if stock_data else None)
        logger.debug("Stock data type: %s", type(stock_data))

        news_payload = {
            "company_name": company_name,
            "news": [d.model_dump(exclude={"raw"}) for d in news_docs],
        }

        return DashboardSearchResponse(
            query=query,
            symbol=symbol,
            company_name=company_name,
            stock_data=stock_data if stock_data else {},
            news=news_payload,
        )
    except Exception as e:
        logger.exception("Dashboard search API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
