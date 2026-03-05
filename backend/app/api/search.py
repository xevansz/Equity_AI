import asyncio

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import (
    get_chat_service,
    get_current_user,
    get_data_service,
    get_database,
    get_news_loader,
)
from app.ingestion.news_loader import NewsLoader
from app.llm.report_generator import generate_equity_report
from app.llm.symbol_resolver import symbol_resolver
from app.logging_config import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.financial import FinancialResponse
from app.schemas.search import SearchResponse
from app.services.chat_service import ChatService
from app.services.data_service import DataService

logger = get_logger(__name__)

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def single_search(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    data_service: DataService = Depends(get_data_service),
    news_loader: NewsLoader = Depends(get_news_loader),
) -> SearchResponse:
    query = request.query

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    symbol = await symbol_resolver(query, db)

    logger.info("Single search called (query=%s symbol=%s)", query, symbol)

    try:
        chat_task = chat_service.process_query(request)
        financial_task = data_service.get_financial_data(symbol)
        news_task = news_loader.load_news(symbol, db=db)

        chat_response, financial_data, news_docs = await asyncio.gather(
            chat_task,
            financial_task,
            news_task,
        )

        research_report = generate_equity_report(symbol, db)

        logger.info("News articles fetched: %s", len(news_docs) if news_docs else 0)

        news_payload = {
            "symbol": symbol,
            "news": [d.model_dump(exclude={"raw"}) for d in news_docs],
        }

        return SearchResponse(
            query=query,
            symbol=symbol,
            chat=ChatResponse(answer=chat_response.answer, sources=chat_response.sources),
            financial=financial_data if isinstance(financial_data, FinancialResponse) else None,
            research=research_report if isinstance(research_report, dict) else {},
            news=news_payload,
        )
    except Exception as e:
        logger.exception("Search API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
