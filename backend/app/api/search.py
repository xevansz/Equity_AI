# api/search.py
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_database, get_current_user
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.mcp.news_api import NewsAPI
from app.services.data_service import DataService
from app.research_engine.report_generator import generate_equity_report
from app.models.conversation import SearchRequest
from app.llm.symbol_resolver import symbol_resolver
import asyncio

router = APIRouter()


@router.post("/search")
async def single_search(
  request: SearchRequest,
  db=Depends(get_database),
  user=Depends(get_current_user),
):
  query = request.query

  symbol = await symbol_resolver(query, db)

  print("\n" + "=" * 90)
  print("SINGLE SEARCH API CALLED")
  print("Company Name  :", query)
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
    news_api = NewsAPI()
    data_service = DataService()

    chat_task = chat_service.process_query(chat_request)
    financial_task = data_service.get_financial_data(symbol)
    news_task = news_api.fetch_news(symbol)

    chat_response, financial_data, news = await asyncio.gather(
      chat_task,
      financial_task,
      news_task,
    )

    research_report = generate_equity_report(symbol, db)

    print(f"NEWS ARTICLES FETCHED: {len(news) if news else 0}")

    return {
      "query": query,
      "symbol": symbol,
      "chat": {
        "answer": chat_response.answer,
        "sources": chat_response.sources if hasattr(chat_response, "sources") else [],
      },
      "financial": financial_data.dict()
      if hasattr(financial_data, "dict")
      else financial_data,
      "research": research_report,
      "news": {"symbol": symbol, "news": news},
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
