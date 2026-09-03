"""FastAPI Web Application definition and static asset mounting."""

import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from docuagent.config.settings import settings
from docuagent.api.routes import chat_router, documents_router

app = FastAPI(
    title=settings.app_name,
    description="Production-ready FastAPI backend for DocuAgent RAG with Streaming and Observability",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/assets") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Include API routers
app.include_router(chat_router)
app.include_router(documents_router)

# Locate Frontend Dist directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
LEGACY_DIST = ROOT_DIR / "dist"

DIST_DIR = FRONTEND_DIST if FRONTEND_DIST.exists() else LEGACY_DIST
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/")
async def serve_index():
    """Serve frontend web application index.html."""
    index_file = DIST_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "DocuAgent API is running. Frontend build not found.",
        "docs": "/docs",
    }


def run_server():
    """Entry point to run FastAPI uvicorn server."""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("docuagent.api.app:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run_server()
