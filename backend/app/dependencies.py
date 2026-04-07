from typing import Any

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
from app.market_data.dispatcher import MarketDataDispatcher
from app.mcp.financial_api import AlphaVantageMCP
from app.mcp.finnhub_api import FinnhubMCP
from app.mcp.news_api import NewsAPI
from app.mcp.sec_api import SECAPI
from app.services.chat_service import ChatService
from app.services.stock_price_service import StockPriceService

security = HTTPBearer()


# Database
def get_database() -> AsyncIOMotorDatabase | None:
    """Get database instance dependency.

    Returns:
        Database instance or None if not connected
    """
    return database.get_database()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, Any]:
    """Get current user from JWT token.

    Args:
        credentials: HTTP authorization credentials with JWT token

    Returns:
        User payload from JWT token

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    """Get user service dependency.

    Args:
        db: Database connection

    Returns:
        UserService instance
    """
    return UserService(db)


def get_conversation_memory(db: AsyncIOMotorDatabase = Depends(get_database)) -> ConversationMemory:
    """Get conversation memory dependency.

    Args:
        db: Database connection

    Returns:
        ConversationMemory instance
    """
    return ConversationMemory(db)


def get_vector_store(request: Request) -> VectorStore:
    """Get vector store dependency.

    Args:
        request: FastAPI request

    Returns:
        VectorStore instance
    """
    client = getattr(request.app.state, "vector_store", None)
    if client is not None:
        return client
    return VectorStore()


def get_vectorstore_api(request: Request) -> VectorStore:
    """Get vector store API dependency.

    Args:
        request: FastAPI request

    Returns:
        VectorStore instance
    """
    return get_vector_store(request)


def get_chat_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
) -> ChatService:
    """Get chat service dependency.

    Args:
        db: Database connection
        user: Current user
        vector_store: Vector store instance

    Returns:
        ChatService instance
    """
    user_id = user.get("email") if isinstance(user, dict) else None
    return ChatService(db, user_id=user_id, vector_store=vector_store)


def get_financial_loader(request: Request) -> FinancialLoader:
    """Get financial loader dependency.

    Args:
        request: FastAPI request

    Returns:
        FinancialLoader instance
    """
    av = get_alpha_vantage()
    return FinancialLoader(av, None)


def get_data_service(
    request: Request,
    financial_loader: FinancialLoader = Depends(get_financial_loader),
) -> StockPriceService:
    """Get data service dependency.

    Args:
        request: FastAPI request
        financial_loader: Financial loader instance

    Returns:
        StockPriceService instance
    """
    market_dispatcher = get_market_dispatcher(request)
    return StockPriceService(financial_loader, market_dispatcher)


def get_news_api() -> NewsAPI:
    """Get News API dependency.

    Returns:
        NewsAPI instance
    """
    return NewsAPI()


def get_news_loader(request: Request) -> NewsLoader:
    """Get news loader dependency.

    Args:
        request: FastAPI request

    Returns:
        NewsLoader instance
    """
    loader = getattr(request.app.state, "news_loader", None)
    if loader is not None:
        return loader
    return NewsLoader(get_news_api())


def get_transcript_loader(request: Request) -> TranscriptLoader:
    """Get transcript loader dependency.

    Args:
        request: FastAPI request

    Returns:
        TranscriptLoader instance
    """
    loader = getattr(request.app.state, "transcript_loader", None)
    if loader is not None:
        return loader
    return TranscriptLoader()


def get_alpha_vantage() -> AlphaVantageMCP:
    """Get Alpha Vantage MCP dependency.

    Returns:
        AlphaVantageMCP instance
    """
    return AlphaVantageMCP()


def get_finnhub(request: Request) -> FinnhubMCP | None:
    """Get Finnhub MCP dependency.

    Args:
        request: FastAPI request

    Returns:
        FinnhubMCP instance or None
    """
    client = getattr(request.app.state, "finnhub", None)
    return client


def get_market_dispatcher(request: Request) -> MarketDataDispatcher:
    """Get market data dispatcher dependency.

    Args:
        request: FastAPI request

    Returns:
        MarketDataDispatcher instance
    """
    dispatcher = getattr(request.app.state, "market_dispatcher", None)
    if dispatcher is not None:
        return dispatcher
    # Fallback: create a basic dispatcher without fallback providers
    return MarketDataDispatcher()


def get_sec_api() -> SECAPI:
    """Get SEC API dependency.

    Returns:
        SECAPI instance
    """
    return SECAPI()


def get_sec_filing_loader(request: Request) -> SECFilingLoader:
    """Get SEC filing loader dependency.

    Args:
        request: FastAPI request

    Returns:
        SECFilingLoader instance
    """
    sec_api = get_sec_api()
    return SECFilingLoader(sec_api)


def get_vector_ingestion_service() -> VectorIngestionService:
    """Get vector ingestion service dependency.

    Returns:
        VectorIngestionService instance
    """
    return VectorIngestionService()


def admin_only(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Verify user is an admin.

    Args:
        user: Current user from JWT token

    Returns:
        User payload if admin

    Raises:
        HTTPException: If user is not an admin
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
