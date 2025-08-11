# Claude Desktop Integration Guide for Kansofy-Trade

## 🚀 Quick Setup

### 1. Configuration Complete ✅
The MCP server is now configured for Claude Desktop integration:
- **Config file**: `~/.config/claude-desktop/claude_desktop_config.json`
- **Python path**: `/Users/vadik/clarity-sandbox/kansofy-trade/venv/bin/python`
- **Working directory**: `/Users/vadik/clarity-sandbox/kansofy-trade`

### 2. MCP Server Status ✅
- **11 production tools** ready for Claude Desktop
- **182 embeddings** stored and operational  
- **Vector search** working with real documents
- **Database initialized** and healthy

## 📋 Available MCP Tools

### Document Intelligence Tools
1. **`search_documents`** - Full-text search with FTS5 support
2. **`vector_search`** - Semantic similarity search using embeddings
3. **`get_document_details`** - Detailed document information and content
4. **`get_document_json`** - Full JSON representation with embeddings
5. **`get_document_tables`** - Extracted tables in multiple formats
6. **`analyze_document_content`** - Pattern analysis and entity extraction

### System Tools  
7. **`get_document_statistics`** - Collection statistics and breakdowns
8. **`get_system_health`** - Health checks and performance metrics
9. **`find_duplicates`** - Content-based duplicate detection
10. **`check_duplicate_by_hash`** - SHA-256 hash duplicate checking
11. **`update_embeddings`** - Batch embedding generation for new documents

## 🔌 Next Steps for Claude Desktop

### Restart Claude Desktop
After saving the configuration file, restart Claude Desktop to load the MCP server.

### Test Integration
In Claude Desktop, try these commands to test the integration:

```
Can you search for documents about "copper trading"?
```

```
What are the statistics for our document collection?
```

```
Check system health and show me performance metrics.
```

```  
Find documents similar to "invoice processing" using vector search.
```

### Expected Results
- Claude Desktop should connect to the MCP server without errors
- All 11 tools should be accessible and functional
- Vector search should return results from 182+ embeddings
- Document upload and processing should work through web interface

## 🏥 Health Check

### Current System Status
- **FastAPI Server**: Running on http://localhost:8000 
- **Database**: SQLite with 182+ document embeddings
- **Vector Store**: Operational with sentence-transformers model
- **MCP Server**: Ready for stdio communication
- **Upload Directory**: `uploads/` with file processing pipeline

### Test Data Available
The system currently has real documents processed with:
- **PDF extraction** using Docling
- **Table extraction** with structured data
- **Vector embeddings** for semantic search
- **Duplicate detection** via SHA-256 hashing
- **Entity extraction** and content analysis

## 🛠️ Troubleshooting

### If MCP Server Doesn't Connect
1. Check Claude Desktop logs for connection errors
2. Verify python path: `/Users/vadik/clarity-sandbox/kansofy-trade/venv/bin/python`
3. Ensure working directory is correct
4. Test MCP server manually: `python mcp_server.py`

### If Tools Don't Work
1. Verify FastAPI server is running on port 8000
2. Check database file exists: `./kansofy_trade.db`
3. Ensure vector store tables are initialized
4. Test with web interface at http://localhost:8000

---

**Status**: Ready for Claude Desktop integration ✅
**Last Updated**: August 10, 2025