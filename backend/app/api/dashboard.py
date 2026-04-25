"""Dashboard API Endpoint"""

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database, get_financial_loader, get_news_loader
from app.exceptions import DatabaseError, ValidationError
from app.ingestion.financial_loader import FinancialLoader
from app.ingestion.news_loader import NewsLoader
from app.llm.symbol_resolver import symbol_resolver
from app.logging_config import get_logger
from app.schemas.dashboard import DashboardSearchRequest, DashboardSearchResponse
from app.schemas.market import Market
from app.services.market_snapshot_service import extract_market_snapshot

logger = get_logger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.post("/search", response_model=DashboardSearchResponse)
async def dashboard_search(
    request: DashboardSearchRequest,
    http_request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
    financial_loader: FinancialLoader = Depends(get_financial_loader),
    news_loader: NewsLoader = Depends(get_news_loader),
    search_status: str = "ok",
) -> DashboardSearchResponse:
    """Dashboard search - returns only stock price data and news (no LLM).

    Args:
        request: Dashboard search request with query
        db: Database connection
        user: Current authenticated user
        financial_loader: Financial data loader service
        news_loader: News loader service
        search_status: Search status indicator

    Returns:
        DashboardSearchResponse with stock data and news

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    query = request.query

    if not query:
        raise ValidationError("query is required")

    if db is None:
        raise DatabaseError("Database not available")

    symbol, company_name = await symbol_resolver(query, db)

    if symbol == "UNKNOWN" or company_name == "UNKNOWN":
        return DashboardSearchResponse(
            query=query,
            symbol="UNKNOWN",
            company_name="UNKNOWN",
            stock_data={},
            news={"company_name": "", "news": []},
            market_snapshot=None,
            search_status="company_not_found",
        )

    logger.info("Dashboard search called (query=%s symbol=%s market=%s)", query, symbol, request.market)

    # Get market dispatcher from app state
    dispatcher = http_request.app.state.market_dispatcher

    # Determine market and exchange
    market_enum = Market.US if request.market.upper() == "US" else Market.INDIA
    exchange = "NSE_EQ" if market_enum == Market.INDIA else None

    try:
        stock_data_task = financial_loader.load_stock_prices(symbol)
        news_task = news_loader.load_news(symbol, company_name, db=db)

        # Fetch intraday data from dispatcher (TwelveData primary)
        intraday_task = dispatcher.get_chart(
            symbol,
            interval="1min",
            outputsize=100,
            market=market_enum,
            exchange=exchange,
        )

        stock_data, news_docs, intraday_data = await asyncio.gather(
            stock_data_task,
            news_task,
            intraday_task,
            return_exceptions=True,
        )

        # Handle exceptions from parallel tasks
        if isinstance(stock_data, Exception):
            logger.error("Error loading stock prices: %s", stock_data)
            stock_data = {}
        if isinstance(news_docs, Exception):
            logger.error("Error loading news: %s", news_docs)
            news_docs = []
        if isinstance(intraday_data, Exception):
            logger.error("Error loading intraday data: %s", intraday_data)
            intraday_data = []

        logger.info("News articles fetched: %s", len(news_docs) if news_docs else 0)
        logger.info("Intraday candles fetched: %s", len(intraday_data) if intraday_data else 0)
        logger.debug("Stock data keys: %s", list(stock_data.keys()) if stock_data else None)
        logger.debug("Stock data type: %s", type(stock_data))

        news_payload = {
            "company_name": company_name,
            "news": [d.model_dump(exclude={"raw"}) for d in news_docs] if news_docs else [],
        }

        # Convert intraday data to list of dicts
        intraday_list = []
        if intraday_data and not isinstance(intraday_data, Exception):
            intraday_list = [
                {
                    "timestamp": point.timestamp,
                    "open": point.open,
                    "high": point.high,
                    "low": point.low,
                    "close": point.close,
                    "volume": point.volume,
                }
                for point in intraday_data
            ]

        market_snapshot = extract_market_snapshot(stock_data, symbol)

        if not stock_data or "Time Series (Daily)" not in stock_data:
            search_status = "no_stock_data"

        return DashboardSearchResponse(
            query=query,
            symbol=symbol,
            company_name=company_name,
            stock_data=stock_data if stock_data else {},
            intraday_data=intraday_list,
            news=news_payload,
            market_snapshot=market_snapshot,
            search_status=search_status,
        )
    except ValidationError as e:
        logger.error("Validation error in dashboard search: %s", e.message)
        raise HTTPException(status_code=400, detail=e.message) from e
    except DatabaseError as e:
        logger.error("Database error in dashboard search: %s", e.message)
        raise HTTPException(status_code=503, detail=e.message) from e
    except Exception as e:
        logger.exception("Dashboard search API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
