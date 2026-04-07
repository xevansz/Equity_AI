import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.api import (
    chat,
    conversations,
    dashboard,
    financial,
    health,
    ingestion,
    news,
    research,
    transcripts,
    unified_search,
    watchlist,
    ws_stream,
)
from app.auth import auth
from app.config import settings
from app.database import close_databases, create_index, database, init_databases
from app.embeddings.vector_store import VectorStore
from app.ingestion.news_loader import NewsLoader
from app.ingestion.transcript_loader import TranscriptLoader
from app.ingestion.warmer import run_warmer
from app.logging_config import configure_logging
from app.market_data.dispatcher import MarketDataDispatcher
from app.market_data.key_rotator import KeyRotatorRegistry
from app.market_data.providers.alpha_vantage import AlphaVantageProvider
from app.market_data.providers.finnhub import FinnhubProvider
from app.mcp.financial_api import AlphaVantageMCP
from app.mcp.finnhub_api import FinnhubMCP
from app.mcp.news_api import NewsAPI
from app.mcp.sec_api import SECAPI

configure_logging()


# lifespan rules
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_databases()
    await create_index()

    # Initialize legacy MCP providers
    app.state.alpha_vantage = AlphaVantageMCP()
    app.state.finnhub = FinnhubMCP(settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else None

    # Initialize KeyRotatorRegistry for TwelveData and Upstox
    twelve_data_keys = [k.strip() for k in settings.TWELVE_DATA_API_KEYS.split(",") if k.strip()]
    upstox_keys = [k.strip() for k in settings.UPSTOX_API_KEYS.split(",") if k.strip()]

    KeyRotatorRegistry.init(
        twelve_data_keys=twelve_data_keys,
        twelve_data_limit=800,  # TwelveData free tier: 800 requests/day
        upstox_keys=upstox_keys,
        upstox_limit=1000,  # Upstox limit (adjust based on your plan)
    )

    # Initialize fallback providers
    alpha_vantage_provider = AlphaVantageProvider(app.state.alpha_vantage)
    finnhub_provider = FinnhubProvider(app.state.finnhub) if app.state.finnhub else None

    # Initialize MarketDataDispatcher with fallback providers
    app.state.market_dispatcher = MarketDataDispatcher(
        alpha_vantage_provider=alpha_vantage_provider,
        finnhub_provider=finnhub_provider,
    )

    app.state.news_api = NewsAPI()
    app.state.news_loader = NewsLoader(app.state.news_api)
    app.state.transcript_loader = TranscriptLoader()
    app.state.sec_api = SECAPI()
    app.state.vector_store = VectorStore()
    app.state.warmer_task = asyncio.create_task(
        run_warmer(database.get_database(), app.state.news_loader, app.state.transcript_loader)
    )

    yield

    # shutdown
    app.state.warmer_task.cancel()

    try:
        await app.state.warmer_task
    except asyncio.CancelledError:
        pass

    await close_databases()

    await app.state.alpha_vantage.close()
    if app.state.finnhub:
        await app.state.finnhub.close()
    await app.state.news_api.close()
    await app.state.sec_api.close()
    await app.state.transcript_loader.close()


# FastAPI app
app = FastAPI(
    title="Conversational Equity Research",
    version="1.0.0",
    description="AI powered stock research platform",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(research.router)
app.include_router(financial.router)
app.include_router(news.router)
app.include_router(transcripts.router)
app.include_router(dashboard.router)
app.include_router(watchlist.router)
app.include_router(conversations.router)
app.include_router(ingestion.router)
app.include_router(unified_search.router)
app.include_router(ws_stream.router)


# root
@app.get("/")
def root():
    # If a built frontend exists, serve its index.html
    dist_index = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist", "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    # If no built frontend, redirect to vite dev server (developer workflow)
    return RedirectResponse(url="http://localhost:3000/")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


# Validation error handler (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


# Generic 500 handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
