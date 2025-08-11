# Kansofy-Trade MCP Server Roadmap

## Current Status ✅
- [x] Document upload via web interface
- [x] Docling integration for advanced text extraction
- [x] Basic MCP server with search and retrieval tools
- [x] SQLite database with document storage
- [x] Web UI at http://localhost:8000

## Next Priority Features 🚀

### 1. Enhanced Document Intelligence (High Priority)
- [ ] **Semantic Search with Embeddings**
  - Add vector search using sentence-transformers
  - Store embeddings in SQLite with sqlite-vss extension
  - Enable similarity search beyond keyword matching

- [ ] **Document Comparison Tool**
  - Compare two documents for differences
  - Find similar documents automatically
  - Track document versions

- [ ] **Structured Data Extraction**
  - Extract tables from documents (Docling already supports this!)
  - Parse invoices, contracts, reports into structured JSON
  - Export to CSV/Excel formats

### 2. MCP Server Enhancements (Medium Priority)
- [ ] **Batch Operations**
  - Process multiple documents at once
  - Bulk search and export
  - Queue management for large uploads

- [ ] **Advanced Analysis Tools**
  - Summarization across multiple documents
  - Trend analysis over time
  - Entity relationship mapping

- [ ] **Real-time Processing Status**
  - WebSocket for live updates
  - Processing progress indicators
  - Error recovery and retry logic

### 3. Integration Features (Medium Priority)
- [ ] **Export/Import Capabilities**
  - Export document collections
  - Import from cloud storage (S3, Google Drive)
  - API endpoints for external systems

- [ ] **Webhook Support**
  - Notify external systems on document events
  - Integration with workflow automation tools
  - Custom processing pipelines

### 4. User Experience (Low Priority)
- [ ] **Advanced Search UI**
  - Search filters and facets
  - Save search queries
  - Search history

- [ ] **Document Tagging**
  - Manual and automatic tags
  - Tag-based organization
  - Smart folders

## Quick Wins 🎯

### 1. Add Document Categories
Simple categorization system for better organization:
```python
# In Document model
category = Column(String(50), index=True)  # invoice, contract, report, etc.
```

### 2. Enable Docling Table Extraction
Docling already extracts tables! Let's expose them:
```python
# In document_processor.py
tables = result.document.tables  # Get extracted tables
# Store in database as JSON
```

### 3. Add Processing Logs UI
Show processing history in the web interface:
```python
# New endpoint in documents.py
@router.get("/documents/{document_id}/logs")
async def get_processing_logs(document_id: int, db: AsyncSession = Depends(get_db)):
    # Return processing logs for debugging
```

## How to Use with Claude Desktop

1. **Configure Claude Desktop:**
   Add to `~/.claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "kansofy-trade": {
         "command": "python3",
         "args": ["/Users/vadik/clarity-sandbox/kansofy-trade/mcp_server.py"],
         "env": {
           "PYTHONPATH": "/Users/vadik/clarity-sandbox/kansofy-trade"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Use these commands in Claude:**
   - "Search my documents for copper invoices"
   - "What documents were uploaded today?"
   - "Show me the content of document ID 1"
   - "Analyze all contracts for payment terms"

## Technical Debt to Address
- [ ] Add proper error handling for FTS5
- [ ] Implement connection pooling
- [ ] Add request rate limiting
- [ ] Improve logging and monitoring
- [ ] Add unit tests for document processor
- [ ] Document API with OpenAPI/Swagger

## Vision 🌟
Transform Kansofy-Trade into a comprehensive document intelligence platform that:
- Understands document content deeply
- Provides intelligent search and analysis
- Integrates seamlessly with AI assistants
- Scales to handle thousands of documents
- Maintains simplicity and ease of use