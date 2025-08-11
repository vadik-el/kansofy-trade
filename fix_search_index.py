#!/usr/bin/env python3
"""Fix the search index by creating the FTS5 table"""

import asyncio
import aiosqlite
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "./kansofy_trade.db"


async def create_fts5_table():
    """Create the FTS5 search table and triggers"""
    
    logger.info("🔧 Creating FTS5 search index...")
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Drop existing table if it exists (to fix schema)
        await db.execute("DROP TABLE IF EXISTS document_search")
        await db.execute("DROP TRIGGER IF EXISTS documents_ai")
        await db.execute("DROP TRIGGER IF EXISTS documents_au") 
        await db.execute("DROP TRIGGER IF EXISTS documents_ad")
        
        # Create the FTS5 virtual table for full-text search
        await db.execute("""
            CREATE VIRTUAL TABLE document_search USING fts5(
                filename,
                content,
                doc_metadata,
                content=documents,
                content_rowid=id
            )
        """)
        
        # Create triggers to keep FTS5 in sync with documents table
        # Trigger for INSERT
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai 
            AFTER INSERT ON documents 
            WHEN NEW.status = 'completed'
            BEGIN
                INSERT INTO document_search(rowid, filename, content, doc_metadata)
                VALUES (NEW.id, NEW.filename, NEW.content, NEW.doc_metadata);
            END
        """)
        
        # Trigger for UPDATE
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au 
            AFTER UPDATE ON documents 
            WHEN NEW.status = 'completed' AND OLD.status != 'completed'
            BEGIN
                INSERT OR REPLACE INTO document_search(rowid, filename, content, doc_metadata)
                VALUES (NEW.id, NEW.filename, NEW.content, NEW.doc_metadata);
            END
        """)
        
        # Trigger for DELETE
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad 
            AFTER DELETE ON documents 
            BEGIN
                DELETE FROM document_search WHERE rowid = OLD.id;
            END
        """)
        
        await db.commit()
        logger.info("✅ FTS5 search table created successfully")
        
        # Populate FTS5 with existing completed documents
        cursor = await db.execute("""
            SELECT COUNT(*) FROM documents WHERE status = 'completed'
        """)
        count = (await cursor.fetchone())[0]
        
        if count > 0:
            logger.info(f"📝 Indexing {count} existing documents...")
            await db.execute("""
                INSERT INTO document_search(rowid, filename, content, doc_metadata)
                SELECT id, filename, content, doc_metadata 
                FROM documents 
                WHERE status = 'completed'
            """)
            await db.commit()
            logger.info(f"✅ Indexed {count} documents")
        else:
            logger.info("📭 No completed documents to index")


async def verify_search_index():
    """Verify the search index is working"""
    
    logger.info("🔍 Verifying search index...")
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if the table exists
        cursor = await db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='document_search'
        """)
        result = await cursor.fetchone()
        
        if result:
            logger.info("✅ Search index table exists")
            
            # Try a test search
            try:
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM document_search
                """)
                count = (await cursor.fetchone())[0]
                logger.info(f"✅ Search index contains {count} documents")
                
                # Test search functionality
                cursor = await db.execute("""
                    SELECT filename FROM document_search 
                    WHERE document_search MATCH 'test' 
                    LIMIT 1
                """)
                result = await cursor.fetchone()
                logger.info("✅ Search functionality verified")
                
            except Exception as e:
                logger.error(f"❌ Search test failed: {e}")
        else:
            logger.error("❌ Search index table does not exist")


async def main():
    """Main function to fix the search index"""
    
    logger.info("=" * 60)
    logger.info("🚀 Kansofy-Trade Search Index Repair Tool")
    logger.info("=" * 60)
    
    # Check if database exists
    db_path = Path(DATABASE_PATH)
    if not db_path.exists():
        logger.error(f"❌ Database not found at {DATABASE_PATH}")
        return
    
    # Create FTS5 table
    await create_fts5_table()
    
    # Verify it's working
    await verify_search_index()
    
    logger.info("=" * 60)
    logger.info("🎉 Search index repair complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())