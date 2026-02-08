"""FastAPI Application Entry Point"""
#main.py

from enum import auto
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings
from app.database import close_databases, init_databases
from app.api import chat, research, financial, news, health, search
from app.auth.auth_router import router as auth_router 
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os



# Create FastAPI app (NO comma here!)
app = FastAPI(
    title="Conversational Equity Research",
    version="1.0.0",
    description="AI powered stock research platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(health.router, prefix="/api", tags=["health"])
#app.include_router(chat.router, prefix="/api", tags=["chat"])
#app.include_router(research.router, prefix="/api", tags=["research"])
#app.include_router(financial.router, prefix="/api", tags=["financial"])
#app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
def root():
    # If a built frontend exists, serve its index.html
    dist_index = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist', 'index.html')
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    # If no built frontend, redirect to vite dev server (developer workflow)
    return RedirectResponse(url="http://localhost:3000/")
    

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

# Startup & shutdown
@app.on_event("startup")
async def startup():
    await init_databases()
    print("🚀 Conversational Equity Research API started")
    # Open browser automatically on startup for convenience in dev.
    # Opening a browser from the FastAPI startup when using the reload watcher
    # can cause subprocess/stdin issues on Windows. Make this opt-in via
    # the environment variable OPEN_BROWSER=1 to avoid reloader problems.
    try:
        if os.environ.get("OPEN_BROWSER") == "1":
            import webbrowser
            host_for_browser = 'localhost' if settings.HOST in ("0.0.0.0", "::") else settings.HOST
            url = f"http://{host_for_browser}:{settings.PORT}/"
            webbrowser.open(url)
    except Exception:
        pass

@app.on_event("shutdown")
async def shutdown():
    await close_databases()

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


# Serve built frontend static files if present
dist_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist')
if os.path.isdir(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
