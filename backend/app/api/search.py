import asyncio

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import (
    get_chat_service,
    get_current_user,
    get_data_service,
    get_database,
    get_news_api,
)
from app.llm.report_generator import generate_equity_report
from app.llm.symbol_resolver import symbol_resolver
from app.mcp.news_api import NewsAPI
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.financial import FinancialResponse
from app.schemas.search import SearchResponse
from app.services.chat_service import ChatService
from app.services.data_service import DataService

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def single_search(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    data_service: DataService = Depends(get_data_service),
    news_api: NewsAPI = Depends(get_news_api),
) -> SearchResponse:
    query = request.query

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    symbol = await symbol_resolver(query, db)

    print("\n" + "=" * 90)
    print("SINGLE SEARCH API CALLED")
    print("Company Name  :", query)
    print("Symbol :", symbol)
    print("=" * 90)

    try:
        chat_task = chat_service.process_query(request)
        financial_task = data_service.get_financial_data(symbol)
        news_task = news_api.fetch_news(symbol)

        chat_response, financial_data, news = await asyncio.gather(
            chat_task,
            financial_task,
            news_task,
        )

        research_report = generate_equity_report(symbol, db)

        print(f"NEWS ARTICLES FETCHED: {len(news) if news else 0}")

        return SearchResponse(
            query=query,
            symbol=symbol,
            chat=ChatResponse(answer=chat_response.answer, sources=chat_response.sources),
            financial=financial_data if isinstance(financial_data, FinancialResponse) else None,
            research=research_report if isinstance(research_report, dict) else {},
            news={"symbol": symbol, "news": news},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
