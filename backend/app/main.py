import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.api import chat, conversations, financial, health, news, research, search, watchlist
from app.auth.auth_router import router as auth_router
from app.config import settings
from app.database import close_databases, create_index_cache, init_databases
from app.logging_config import configure_logging
from app.mcp.financial_api import alpha_vantage
from app.mcp.news_api import NewsAPI
from app.mcp.sec_api import sec_api

configure_logging()


# lifespan rules
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_databases()
    await create_index_cache()
    app.state.news_api = NewsAPI()
    yield
    # shutdown
    await close_databases()
    await alpha_vantage.close()
    await app.state.news_api.close()
    await sec_api.close()


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
API_PREFIX = "/api"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(research.router, prefix=API_PREFIX)
app.include_router(financial.router, prefix=API_PREFIX)
app.include_router(news.router, prefix=API_PREFIX)
app.include_router(search.router, prefix=API_PREFIX)
app.include_router(watchlist.router, prefix=API_PREFIX)
app.include_router(conversations.router, prefix=API_PREFIX)


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
