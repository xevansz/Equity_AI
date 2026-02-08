#api/search.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_database
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.mcp.news_api import NewsAPI
from app.services.data_service import DataService
from app.research_engine.report_generator import generate_equity_report

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    symbol: Optional[str] = None

@router.post("/search")
async def single_search(request: SearchRequest, db = Depends(get_database)):
    query = request.query
    symbol = (request.symbol or request.query).upper()

    # simple alias mapping
    SYMBOL_ALIASES = {
    "APPLE": "AAPL",
    "GOOGLE": "GOOGL",
    "TESLA": "TSLA",
    "MICROSOFT": "MSFT",
    "AMAZON": "AMZN",}

    symbol = SYMBOL_ALIASES.get(symbol, symbol)


    print("\n" + "=" * 90)
    print("🔍 SINGLE SEARCH API CALLED")
    print("Query  :", query)
    print("Symbol :", symbol)
    print("=" * 90)

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # Chat search
        chat_request = ChatRequest(query=query)
        chat_service = ChatService(db)
        chat_response = await chat_service.process_query(chat_request)
        print("✅ CHAT ANSWER:", chat_response.answer)
        
        # Financial data
        data_service = DataService()
        financial_data = await data_service.get_financial_data(symbol)
        
        # Research report
        research_report = generate_equity_report(symbol, db)
        
        # News
        news_api = NewsAPI()
        news = await news_api.fetch_news(symbol)
        print(f"✅ NEWS ARTICLES FETCHED: {len(news) if news else 0}")
        
        return {
            "query": query,
            "symbol": symbol,
            "chat": {
                "answer": chat_response.answer,
                "sources": chat_response.sources if hasattr(chat_response, 'sources') else []
            },
            "financial": financial_data.dict() if hasattr(financial_data, 'dict') else financial_data,
            "research": research_report,
            "news": {"symbol": symbol, "news": news}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
