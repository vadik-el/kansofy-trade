# Vector Store & Hash-Based Storage for Kansofy-Trade MCP Server

## Overview
The vector store has been successfully implemented in your Kansofy-Trade MCP server with enhanced features:
- **Semantic search** using document embeddings
- **SHA-256 hashing** for duplicate detection at file and chunk levels
- **Full JSON storage** for complete document representation in SQLite
- **Chunk-level hashing** for granular tracking and deduplication
- **Comprehensive metadata** stored alongside embeddings

## Features Implemented

### 1. Vector Store Core (`app/core/vector_store.py`)
- **Embedding Generation**: Uses `sentence-transformers` (all-MiniLM-L6-v2 model) for generating document embeddings
- **Text Chunking**: Smart chunking with overlap for better context preservation
- **SQLite Storage**: Embeddings stored as JSON arrays in SQLite database
- **Cosine Similarity**: Vector similarity search implementation
- **Duplicate Detection**: Find similar/duplicate documents based on content

### 2. Database Schema

#### Document Embeddings Table
```sql
CREATE TABLE document_embeddings (
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
```

#### Documents Table Enhancement
```sql
-- Added to documents table:
file_hash VARCHAR(64)  -- SHA-256 hash of file content
full_text_json JSON    -- Complete document data including chunks and embeddings
```

### 3. MCP Server Tools

#### `vector_search`
Search documents using semantic similarity:
```
"Find documents about copper invoices"
"Search for shipping documents mentioning vessels"
```

#### `find_duplicates`
Find potential duplicate documents based on embeddings:
```
"Find duplicates of document ID 5"
```

#### `update_embeddings`
Generate embeddings for new documents:
```
"Update embeddings for all documents"
```

#### `get_document_json`
Retrieve complete JSON representation of a document:
```
"Get JSON data for document ID 7"
```

#### `check_duplicate_by_hash`
Check if a document with the same hash already exists:
```
"Check if file hash abc123... already exists"
```

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. The vector store will be initialized automatically when starting the MCP server.

## Usage

### Starting the Server
```bash
python mcp_server.py
```

### In Claude Desktop
After configuring the MCP server in Claude Desktop, you can use natural language commands:

- **Semantic Search**: "Find all documents related to aluminum trading"
- **Duplicate Detection**: "Check if document 3 has any duplicates"
- **Update Embeddings**: "Generate embeddings for new documents"

## How It Works

1. **Document Upload**: When a document is uploaded and processed, text is extracted using Docling
2. **Hash Generation**: 
   - File hash (SHA-256) generated from file content for deduplication
   - Chunk hashes generated for each text chunk (document_id:chunk_index:text)
3. **Chunking**: Text is split into overlapping chunks (512 chars with 50 char overlap)
4. **Embedding Generation**: Each chunk is converted to a 384-dimensional vector
5. **Storage**: 
   - Embeddings stored in SQLite as JSON arrays with chunk hashes
   - Full document JSON stored in `full_text_json` column with complete representation
   - Metadata preserved alongside embeddings
6. **Search**: Query text is embedded and compared against stored embeddings using cosine similarity
7. **Results**: Most similar chunks are returned with relevance scores
8. **Duplicate Detection**: File and chunk hashes enable efficient duplicate identification

## Performance Considerations

- **Model**: all-MiniLM-L6-v2 is lightweight (80MB) but effective
- **Chunking**: 512 character chunks balance context and performance
- **Storage**: JSON arrays in SQLite work well for small-medium collections
- **For larger collections** (>10,000 documents), consider:
  - Using a dedicated vector database (Qdrant, Pinecone, Weaviate)
  - Implementing batch processing for embeddings
  - Adding caching for frequently searched queries

## Next Steps

1. **Test the Implementation**:
   - Upload some documents through the web interface
   - Run `update_embeddings` tool to generate vectors
   - Try semantic search queries

2. **Monitor Performance**:
   - Check embedding generation time
   - Monitor search response times
   - Track storage usage

3. **Future Enhancements**:
   - Add support for different embedding models
   - Implement hybrid search (combining keyword and vector search)
   - Add embedding caching for better performance
   - Consider migrating to sqlite-vss extension for better vector operations

## JSON Storage Structure

The `full_text_json` column stores a comprehensive document representation:

```json
{
  "document_id": 1,
  "document_hash": "sha256_hash_of_content",
  "content": "full document text",
  "content_length": 2048,
  "chunks_count": 5,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimensions": 384,
  "metadata": {
    "category": "invoice",
    "original_filename": "invoice_2024.pdf",
    "content_type": "application/pdf",
    "file_size": 102400,
    "processing_time": 1.23
  },
  "chunks": [
    {
      "index": 0,
      "hash": "chunk_sha256_hash",
      "text": "chunk text content",
      "length": 512,
      "embedding": [0.123, -0.456, ...]
    }
  ],
  "created_at": "2024-01-15T10:30:00"
}
```

## Hash-Based Features

### File Hash
- Generated using SHA-256 on file content
- Stored in `documents.file_hash` column
- Used for whole-file duplicate detection
- Generated during document processing

### Chunk Hash
- Generated using SHA-256 on `document_id:chunk_index:chunk_text`
- Stored in `document_embeddings.chunk_hash` column
- Ensures unique chunks across documents
- Enables granular duplicate detection

### Duplicate Detection Workflow
1. **File-Level**: Check `file_hash` before processing new documents
2. **Chunk-Level**: Identify similar content across different documents
3. **Semantic**: Use embeddings to find conceptually similar documents

## Troubleshooting

### If embeddings are not generating:
1. Check that sentence-transformers is installed
2. Verify the model downloads successfully on first run
3. Check logs for any error messages

### If search returns no results:
1. Ensure embeddings have been generated (`update_embeddings` tool)
2. Try lowering the similarity threshold
3. Check that documents have been processed successfully

### If duplicate detection fails:
1. Verify hashes are being generated during document processing
2. Check that `file_hash` column is populated in documents table
3. Ensure chunk hashes are unique in document_embeddings table

### If performance is slow:
1. Consider reducing chunk size
2. Implement result caching
3. Use a smaller embedding model if needed
4. Add indexes on hash columns if not present