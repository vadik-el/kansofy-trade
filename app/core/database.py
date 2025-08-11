"""
Database configuration and initialization for Kansofy-Trade
Uses SQLite with FTS5 for full-text search capabilities
"""

import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SQLAlchemy Base
Base = declarative_base()

# Import models so they are registered with Base.metadata
# This ensures tables are created when init_database() is called
from app.models.document import Document, DocumentProcessingLog

# Database engines
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_engine = create_async_engine(
    settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.debug,
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def init_database() -> None:
    """Initialize database with tables and FTS5 setup"""
    logger.info("Initializing database...")
    
    # Create database file if it doesn't exist
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(exist_ok=True)
    
    # Create tables using SQLAlchemy
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize FTS5 and other SQLite-specific features
    await _init_sqlite_features()
    
    logger.info("Database initialized successfully")


async def _init_sqlite_features() -> None:
    """Initialize SQLite-specific features like FTS5"""
    async with aiosqlite.connect(settings.database_path) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create FTS5 search table for full-text search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_search USING fts5(
                filename,
                content,
                doc_metadata,
                content=documents,
                content_rowid=id
            )
        """)
        
        # Create triggers to keep FTS5 in sync
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai 
            AFTER INSERT ON documents 
            WHEN NEW.status = 'completed'
            BEGIN
                INSERT INTO document_search(rowid, filename, content, doc_metadata)
                VALUES (NEW.id, NEW.filename, NEW.content, NEW.doc_metadata);
            END
        """)
        
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au 
            AFTER UPDATE ON documents 
            WHEN NEW.status = 'completed' AND OLD.status != 'completed'
            BEGIN
                INSERT OR REPLACE INTO document_search(rowid, filename, content, doc_metadata)
                VALUES (NEW.id, NEW.filename, NEW.content, NEW.doc_metadata);
            END
        """)
        
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad 
            AFTER DELETE ON documents 
            BEGIN
                DELETE FROM document_search WHERE rowid = OLD.id;
            END
        """)
        
        await db.commit()
        logger.info("✅ FTS5 search index initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """Context manager for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Get synchronous database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def test_database_connection() -> bool:
    """Test database connectivity"""
    try:
        async with get_db_context() as db:
            result = await db.execute(text("SELECT 1"))
            await result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def execute_raw_sql(query: str, params=None) -> list:
    """Execute raw SQL query with optional parameters (list/tuple or dict)"""
    async with aiosqlite.connect(settings.database_path) as db:
        # Set row factory to get dictionary-like rows
        db.row_factory = aiosqlite.Row
        
        if params:
            cursor = await db.execute(query, params)
        else:
            cursor = await db.execute(query)
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []


async def search_documents_fts5(search_term: str, limit: int = 50) -> list:
    """Search documents using FTS5 full-text search"""
    query = """
        SELECT 
            d.id, d.filename, d.file_size, d.uploaded_at, d.content_type,
            snippet(document_search, 2, '<mark>', '</mark>', '...', 20) as snippet,
            rank as relevance_score
        FROM document_search 
        JOIN documents d ON d.id = document_search.rowid
        WHERE document_search MATCH ?
        ORDER BY rank
        LIMIT ?
    """
    
    return await execute_raw_sql(query, (search_term, limit))