"""
Search endpoints for Kansofy-Trade

Full-text search using SQLite FTS5 and vector similarity search for document retrieval.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, search_documents_fts5
from app.core.vector_store import search_similar_documents
from app.models.document import DocumentSearchResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search", response_model=List[DocumentSearchResult])
async def search_documents(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=500),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentSearchResult]:
    """
    Search documents using full-text search.
    
    Supports:
    - Simple text queries: "invoice copper"
    - Phrase queries: "purchase order" 
    - Boolean operators: "copper AND invoice"
    - Wildcard matching: "ship*"
    """
    
    try:
        logger.info(f"Searching documents for query: '{q}' (limit: {limit})")
        
        # Execute FTS5 search
        results = await search_documents_fts5(q, limit)
        
        # Convert to response models
        search_results = [
            DocumentSearchResult(
                id=row['id'],
                filename=row['filename'],
                file_size=row['file_size'],
                uploaded_at=row['uploaded_at'],
                content_type=row.get('content_type'),
                snippet=row.get('snippet', ''),
                relevance_score=float(row.get('relevance_score', 0.0))
            )
            for row in results
        ]
        
        logger.info(f"Found {len(search_results)} documents matching query")
        return search_results
        
    except Exception as e:
        logger.error(f"Search query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Search operation failed. Please try again."
        )


@router.get("/search/vector")
async def vector_search(
    query: str = Query(..., description="Search query for vector similarity", min_length=1, max_length=500),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=100),
    threshold: float = Query(0.5, description="Minimum similarity score", ge=0.0, le=1.0)
):
    """
    Search documents using vector similarity.
    
    Uses sentence embeddings to find semantically similar document chunks.
    Returns chunks with similarity scores and document metadata.
    """
    
    try:
        logger.info(f"Vector search for query: '{query}' (limit: {limit}, threshold: {threshold})")
        
        # Execute vector similarity search
        results = await search_similar_documents(query, limit, threshold)
        
        # Convert to consistent response format matching test expectations
        search_results = []
        for result in results:
            search_results.append({
                "document_id": result["document_id"],
                "chunk_text": result["chunk_text"],
                "similarity_score": result["similarity_score"],
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "uploaded_at": result["uploaded_at"]
            })
        
        logger.info(f"Found {len(search_results)} similar document chunks")
        return search_results
        
    except Exception as e:
        logger.error(f"Vector search query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Vector search operation failed. Please try again."
        )


@router.get("/search/suggest")
async def search_suggestions(
    q: str = Query(..., description="Partial search query", min_length=1, max_length=100),
    limit: int = Query(10, description="Maximum suggestions", ge=1, le=20)
) -> List[str]:
    """
    Get search suggestions based on document content.
    
    Returns common terms and phrases that match the partial query.
    """
    
    # For now, return simple suggestions
    # In production, this could analyze document content for better suggestions
    suggestions = []
    
    if "inv" in q.lower():
        suggestions.extend(["invoice", "invoice number", "invoice date"])
    if "ship" in q.lower():
        suggestions.extend(["shipping", "shipment", "ship date"])
    if "cop" in q.lower():
        suggestions.extend(["copper", "copper concentrate"])
    if "con" in q.lower():
        suggestions.extend(["contract", "container", "concentrate"])
    
    return suggestions[:limit]


@router.get("/search/stats")
async def search_statistics(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Get search and indexing statistics.
    """
    
    try:
        from app.core.database import execute_raw_sql
        
        # Get FTS5 index statistics
        stats_query = """
            SELECT 
                COUNT(*) as indexed_documents,
                SUM(LENGTH(content)) as total_content_length,
                AVG(LENGTH(content)) as avg_content_length
            FROM document_search
        """
        
        stats_result = await execute_raw_sql(stats_query)
        stats = stats_result[0] if stats_result else {}
        
        return {
            "indexed_documents": stats.get('indexed_documents', 0),
            "total_content_length": stats.get('total_content_length', 0),
            "avg_content_length": round(stats.get('avg_content_length', 0), 2),
            "search_features": [
                "Full-text search",
                "Phrase matching", 
                "Boolean operators",
                "Wildcard search",
                "Relevance ranking"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get search statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve search statistics"
        )