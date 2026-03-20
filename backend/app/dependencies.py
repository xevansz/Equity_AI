from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.jwt_handler import verify_token
from app.auth.user_service import UserService
from app.conversational.memory import ConversationMemory
from app.database import database
from app.embeddings.vector_store import VectorStore
from app.ingestion.financial_loader import FinancialLoader
from app.ingestion.news_loader import NewsLoader
from app.ingestion.sec_filing_loader import SECFilingLoader
from app.ingestion.transcript_loader import TranscriptLoader
from app.ingestion.vector_ingestion_service import VectorIngestionService
from app.mcp.financial_api import AlphaVantageMCP
from app.mcp.finnhub_api import FinnhubMCP
from app.mcp.news_api import NewsAPI
from app.mcp.sec_api import SECAPI
from app.services.chat_service import ChatService
from app.services.data_service import DataService
from app.services.stock_price_service import StockPriceService

security = HTTPBearer()


# Database
def get_database():
    """returns the MongoDB database instance"""
    return database.get_database()


# JWT Auth
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """returns the current user from the JWT token"""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    return UserService(db)


def get_conversation_memory(db: AsyncIOMotorDatabase = Depends(get_database)) -> ConversationMemory:
    return ConversationMemory(db)


def get_vector_store(request: Request) -> VectorStore:
    client = getattr(request.app.state, "vector_store", None)
    if client is not None:
        return client
    return VectorStore()


def get_vectorstore_api(request: Request) -> VectorStore:
    return get_vector_store(request)


def get_chat_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
) -> ChatService:
    user_id = user.get("email") if isinstance(user, dict) else None
    return ChatService(db, user_id=user_id, vector_store=vector_store)


def get_financial_loader(request: Request) -> FinancialLoader:
    av = get_alpha_vantage(request)
    stock_price_service = get_stock_price_service(request)
    return FinancialLoader(av, stock_price_service)


def get_data_service(
    request: Request,
    financial_loader: FinancialLoader = Depends(get_financial_loader),
) -> DataService:
    stock_price_service = get_stock_price_service(request)
    return DataService(financial_loader, stock_price_service)


def get_news_api(request: Request) -> NewsAPI:
    client = getattr(request.app.state, "news_api", None)
    if client is not None:
        return client
    return NewsAPI()


def get_news_loader(request: Request) -> NewsLoader:
    loader = getattr(request.app.state, "news_loader", None)
    if loader is not None:
        return loader
    return NewsLoader(get_news_api(request))


def get_transcript_loader(request: Request) -> TranscriptLoader:
    loader = getattr(request.app.state, "transcript_loader", None)
    if loader is not None:
        return loader
    return TranscriptLoader()


def get_alpha_vantage(request: Request) -> AlphaVantageMCP:
    client = getattr(request.app.state, "alpha_vantage", None)
    if client is not None:
        return client
    return AlphaVantageMCP()


def get_finnhub(request: Request) -> FinnhubMCP | None:
    client = getattr(request.app.state, "finnhub", None)
    return client


def get_stock_price_service(request: Request) -> StockPriceService:
    av = get_alpha_vantage(request)
    finnhub = get_finnhub(request)
    return StockPriceService(av, finnhub)


def get_sec_api(request: Request) -> SECAPI:
    client = getattr(request.app.state, "sec_api", None)
    if client is not None:
        return client
    return SECAPI()


def get_sec_filing_loader(request: Request) -> SECFilingLoader:
    sec_api = get_sec_api(request)
    return SECFilingLoader(sec_api)


def get_vector_ingestion_service() -> VectorIngestionService:
    return VectorIngestionService()


# Admin only
def admin_only(user=Depends(get_current_user)):
    """returns the current user if they are an admin"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
