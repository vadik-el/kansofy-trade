"""
Kansofy-Trade: FastAPI Main Application

The open-source MCP runtime for document intelligence.
Transform your supply chain documents into AI-ready knowledge.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import get_settings
from app.core.database import init_database
from app.api.routes import documents, health, search
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Kansofy-Trade...")
    
    # Initialize database
    await init_database()
    logger.info("📊 Database initialized")
    
    # Initialize vector store
    from app.core.vector_store import init_vector_store
    await init_vector_store()
    logger.info("🔍 Vector store initialized")
    
    # Create upload directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"📁 Upload directory ready: {upload_dir}")
    
    yield
    
    logger.info("🛑 Shutting down Kansofy-Trade")


# Initialize FastAPI app
app = FastAPI(
    title="Kansofy-Trade",
    description="The Open-Source MCP Runtime for Document Intelligence",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="app/templates")

# Mount static files if directory exists
static_dir = Path("app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API Routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Home page with simple document upload interface"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Kansofy-Trade",
            "description": "Transform your documents into AI-ready knowledge"
        }
    )


@app.get("/api/v1")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Kansofy-Trade API",
        "version": "1.0.0",
        "description": "The Open-Source MCP Runtime for Document Intelligence",
        "endpoints": {
            "health": "/api/v1/health",
            "documents": "/api/v1/documents",
            "search": "/api/v1/search",
            "docs": "/api/docs"
        },
        "mcp_server": {
            "enabled": True,
            "port": settings.mcp_server_port,
            "tools_count": 5
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )