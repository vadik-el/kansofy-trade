"""
Vector store implementation for document embeddings
Uses sentence-transformers for generating embeddings
Stores vectors in SQLite with JSON for simple vector similarity search
"""

import json
import hashlib
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import aiosqlite
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.database import execute_raw_sql

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize the embedding model
# Using a lightweight but effective model for document embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
embedding_model = None

def get_embedding_model():
    """Get or initialize the embedding model"""
    global embedding_model
    if embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return embedding_model


def generate_text_hash(text: str) -> str:
    """
    Generate SHA-256 hash of text content
    
    Args:
        text: Text to hash
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_chunk_hash(document_id: int, chunk_index: int, chunk_text: str) -> str:
    """
    Generate unique hash for a document chunk
    
    Args:
        document_id: ID of the document
        chunk_index: Index of the chunk
        chunk_text: Text content of the chunk
    
    Returns:
        Hexadecimal hash string
    """
    combined = f"{document_id}:{chunk_index}:{chunk_text}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


async def init_vector_store():
    """Initialize vector store tables in SQLite with enhanced JSON storage"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS document_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_hash TEXT NOT NULL,  -- SHA-256 hash of chunk
        chunk_text TEXT NOT NULL,
        embedding JSON NOT NULL,  -- JSON array of float values
        embedding_model TEXT NOT NULL,
        metadata JSON,  -- Additional metadata as JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
        UNIQUE(document_id, chunk_index),
        UNIQUE(chunk_hash)
    );
    
    CREATE INDEX IF NOT EXISTS idx_document_embeddings_doc_id 
    ON document_embeddings(document_id);
    
    CREATE INDEX IF NOT EXISTS idx_document_embeddings_created 
    ON document_embeddings(created_at);
    
    CREATE INDEX IF NOT EXISTS idx_document_embeddings_chunk_hash
    ON document_embeddings(chunk_hash);
    """
    
    async with aiosqlite.connect(settings.database_path) as db:
        await db.executescript(create_table_query)
        await db.commit()
    
    logger.info("Vector store tables initialized")


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for embedding
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to find a sentence boundary near the end
        if end < text_length:
            # Look for sentence endings
            for delimiter in ['. ', '! ', '? ', '\n\n', '\n']:
                delimiter_pos = text.rfind(delimiter, start, end)
                if delimiter_pos != -1 and delimiter_pos > start + chunk_size // 2:
                    end = delimiter_pos + len(delimiter)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + 1, end - overlap)
    
    return chunks


async def generate_document_embeddings(document_id: int, content: str, metadata: Optional[Dict] = None) -> Dict:
    """
    Generate and store embeddings for a document with hash and JSON storage
    
    Args:
        document_id: ID of the document
        content: Text content to embed
        metadata: Optional metadata to store with embeddings
    
    Returns:
        Dictionary containing embedding statistics and full document JSON
    """
    if not content:
        logger.warning(f"No content to embed for document {document_id}")
        return {"embeddings_count": 0, "document_hash": None, "full_json": None}
    
    try:
        # Generate document hash
        document_hash = generate_text_hash(content)
        
        # Get embedding model
        model = get_embedding_model()
        
        # Chunk the text
        chunks = chunk_text(content)
        logger.info(f"Document {document_id}: Created {len(chunks)} chunks")
        
        if not chunks:
            return {"embeddings_count": 0, "document_hash": document_hash, "full_json": None}
        
        # Generate embeddings for all chunks
        embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        
        # Prepare full document JSON
        full_document_json = {
            "document_id": document_id,
            "document_hash": document_hash,
            "content": content,
            "content_length": len(content),
            "chunks_count": len(chunks),
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimensions": embeddings[0].shape[0] if len(embeddings) > 0 else 0,
            "metadata": metadata or {},
            "chunks": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Store embeddings in database
        async with aiosqlite.connect(settings.database_path) as db:
            # Delete existing embeddings for this document
            await db.execute(
                "DELETE FROM document_embeddings WHERE document_id = ?",
                (document_id,)
            )
            
            # Insert new embeddings with hashes
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_hash = generate_chunk_hash(document_id, idx, chunk)
                embedding_list = embedding.tolist()
                
                # Add chunk to full document JSON
                full_document_json["chunks"].append({
                    "index": idx,
                    "hash": chunk_hash,
                    "text": chunk,
                    "length": len(chunk),
                    "embedding": embedding_list
                })
                
                # Prepare chunk metadata
                chunk_metadata = {
                    "chunk_length": len(chunk),
                    "position": idx,
                    "total_chunks": len(chunks)
                }
                
                await db.execute(
                    """
                    INSERT INTO document_embeddings 
                    (document_id, chunk_index, chunk_hash, chunk_text, embedding, embedding_model, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        document_id, 
                        idx, 
                        chunk_hash,
                        chunk, 
                        json.dumps(embedding_list), 
                        EMBEDDING_MODEL,
                        json.dumps(chunk_metadata)
                    )
                )
            
            # Update document with full JSON and hash
            await db.execute(
                """
                UPDATE documents 
                SET full_text_json = ?, file_hash = ?
                WHERE id = ?
                """,
                (json.dumps(full_document_json), document_hash, document_id)
            )
            
            await db.commit()
        
        logger.info(f"Stored {len(chunks)} embeddings for document {document_id} with hash {document_hash[:8]}...")
        
        return {
            "embeddings_count": len(chunks),
            "document_hash": document_hash,
            "full_json": full_document_json
        }
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings for document {document_id}: {e}")
        raise


async def search_similar_documents(
    query: str, 
    limit: int = 10, 
    threshold: float = 0.5
) -> List[Dict]:
    """
    Search for documents similar to the query using vector similarity
    
    Args:
        query: Search query text
        limit: Maximum number of results
        threshold: Minimum similarity score (0-1)
    
    Returns:
        List of similar document chunks with metadata
    """
    try:
        # Generate embedding for query
        model = get_embedding_model()
        query_embedding = model.encode(query, convert_to_numpy=True)
        
        # Fetch all embeddings from database
        # Note: For production, consider using a proper vector database
        fetch_query = """
        SELECT 
            de.id,
            de.document_id,
            de.chunk_index,
            de.chunk_text,
            de.embedding,
            d.filename,
            d.uploaded_at
        FROM document_embeddings de
        JOIN documents d ON d.id = de.document_id
        WHERE d.status = 'completed'
        """
        
        results = await execute_raw_sql(fetch_query, [])
        
        if not results:
            return []
        
        # Calculate similarities
        similarities = []
        for row in results:
            try:
                # Parse stored embedding
                stored_embedding = np.array(json.loads(row['embedding']))
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, stored_embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        'id': row['id'],
                        'document_id': row['document_id'],
                        'chunk_index': row['chunk_index'],
                        'chunk_text': row['chunk_text'],
                        'filename': row['filename'],
                        'uploaded_at': row['uploaded_at'],
                        'similarity_score': float(similarity)
                    })
            except Exception as e:
                logger.warning(f"Failed to process embedding {row['id']}: {e}")
                continue
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:limit]
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity score (0-1)
    """
    # Normalize vectors
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)
    
    # Convert to 0-1 range
    return (similarity + 1) / 2


async def find_duplicate_documents(
    document_id: int, 
    threshold: float = 0.9
) -> List[Dict]:
    """
    Find potential duplicate documents based on embedding similarity
    
    Args:
        document_id: ID of the document to check
        threshold: Similarity threshold for duplicates (0-1)
    
    Returns:
        List of potential duplicate documents
    """
    try:
        # Get embeddings for the target document
        target_query = """
        SELECT chunk_text, embedding
        FROM document_embeddings
        WHERE document_id = ?
        ORDER BY chunk_index
        """
        
        target_embeddings = await execute_raw_sql(target_query, (document_id,))
        
        if not target_embeddings:
            return []
        
        # Combine chunk texts for similarity search
        combined_text = " ".join([chunk['chunk_text'] for chunk in target_embeddings[:3]])
        
        # Search for similar documents
        similar_docs = await search_similar_documents(
            combined_text, 
            limit=20, 
            threshold=threshold
        )
        
        # Group by document and filter out the source document
        document_scores = {}
        for result in similar_docs:
            if result['document_id'] != document_id:
                doc_id = result['document_id']
                if doc_id not in document_scores:
                    document_scores[doc_id] = {
                        'document_id': doc_id,
                        'filename': result['filename'],
                        'max_similarity': result['similarity_score'],
                        'matching_chunks': 1
                    }
                else:
                    document_scores[doc_id]['max_similarity'] = max(
                        document_scores[doc_id]['max_similarity'],
                        result['similarity_score']
                    )
                    document_scores[doc_id]['matching_chunks'] += 1
        
        # Convert to list and sort by similarity
        duplicates = list(document_scores.values())
        duplicates.sort(key=lambda x: x['max_similarity'], reverse=True)
        
        return duplicates
        
    except Exception as e:
        logger.error(f"Duplicate detection failed for document {document_id}: {e}")
        raise


async def update_all_embeddings():
    """
    Update embeddings for all documents that don't have them yet
    """
    try:
        # Find documents without embeddings
        query = """
        SELECT d.id, d.content
        FROM documents d
        LEFT JOIN document_embeddings de ON d.id = de.document_id
        WHERE d.status = 'completed' 
          AND d.content IS NOT NULL
          AND de.id IS NULL
        GROUP BY d.id
        """
        
        documents = await execute_raw_sql(query, [])
        
        if not documents:
            logger.info("All documents already have embeddings")
            return 0
        
        logger.info(f"Updating embeddings for {len(documents)} documents")
        
        total_embeddings = 0
        for doc in documents:
            try:
                count = await generate_document_embeddings(
                    doc['id'], 
                    doc['content']
                )
                total_embeddings += count
            except Exception as e:
                logger.error(f"Failed to update embeddings for document {doc['id']}: {e}")
                continue
        
        logger.info(f"Created {total_embeddings} total embeddings")
        return total_embeddings
        
    except Exception as e:
        logger.error(f"Batch embedding update failed: {e}")
        raise