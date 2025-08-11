# Engine Troubleshooting Guide 🔧

**Debugging the deterministic document engine. No AI mysteries - just predictable operations.**

## Table of Contents
- [Engine vs Brain Issues](#engine-vs-brain-issues)
- [Quick Fixes](#quick-fixes)
- [Common Issues](#common-issues)
  - [Installation Problems](#installation-problems)
  - [Claude Desktop Integration](#claude-desktop-integration)
  - [Document Processing](#document-processing)
  - [Search Issues](#search-issues)
  - [Performance Problems](#performance-problems)
- [Debug Commands](#debug-commands)
- [Error Messages](#error-messages)
- [FAQ](#faq)
- [Advanced Debugging](#advanced-debugging)
- [Getting Help](#getting-help)

## Engine vs Brain Issues

### Understanding What Can Go Wrong

**Engine Issues (This Project)**:
- ✅ Deterministic - same input always produces same error
- ✅ Predictable - errors are reproducible
- ✅ Debuggable - clear error messages, no AI black box
- ✅ Local - all issues are on your machine

**Brain Issues (AI Layer)**:
- ❌ Variable responses from AI
- ❌ API rate limits or quotas
- ❌ Network connectivity to AI services
- ❌ AI model hallucinations

**If your issue is inconsistent or varies between runs, it's likely a Brain (AI) issue, not an Engine issue.**

## Quick Fixes

| Problem | Quick Solution |
|---------|---------------|
| MCP client can't find engine | Restart your MCP client completely |
| Upload fails | Check file size (<50MB) and format |
| Search returns nothing | Documents processed? This is SQL, not AI search |
| Slow performance | Pre-compute embeddings, check SQLite performance |
| Database locked | Close other connections, restart server |
| Import errors | Activate virtual environment, reinstall requirements |

## Common Issues

### Installation Problems

#### Issue: "ModuleNotFoundError: No module named 'mcp'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solutions:**
```bash
# 1. Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 2. Reinstall MCP
pip install mcp --force-reinstall

# 3. Verify installation
python -c "import mcp; print('MCP installed:', mcp.__version__)"
```

#### Issue: "sqlite3.OperationalError: unable to open database file"

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solutions:**
```bash
# 1. Check file permissions
ls -la kansofy_trade.db
chmod 664 kansofy_trade.db

# 2. Check directory permissions
chmod 755 .

# 3. Initialize database
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

#### Issue: Package installation fails with SSL error

**Symptoms:**
```
pip._vendor.urllib3.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**
```bash
# Option 1: Use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Option 2: Upgrade certificates
pip install --upgrade certifi

# Option 3: Use different index
pip install --index-url=https://pypi.python.org/simple/ -r requirements.txt
```

### MCP Client Integration

#### Issue: MCP client doesn't show engine operations

**Symptoms:**
- AI responds "I don't have access to MCP tools"
- Engine operations don't appear in capability list

**Solutions:**

1. **Verify configuration syntax:**
```bash
# Check JSON is valid
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Should output formatted JSON without errors
```

2. **Check configuration path:**
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["/absolute/path/to/kansofy-trade/mcp_server.py"]
    }
  }
}
```
**Important**: Path must be absolute, not relative!

3. **Test MCP server directly:**
```bash
cd /path/to/kansofy-trade
python mcp_server.py
# Should see: "Starting Kansofy-Trade MCP Server..."
```

4. **Check MCP client logs:**
```bash
# Claude Desktop (macOS)
tail -f ~/Library/Logs/Claude/mcp-server.log
# Other clients - check respective logs

# Look for errors like:
# - "Failed to start server"
# - "Python not found"
# - "Permission denied"
```

5. **Complete restart:**
```bash
# 1. Quit MCP client completely
# 2. Check no client processes running
ps aux | grep [client-name]
# 3. Start MCP client fresh
```

#### Issue: "Failed to start MCP server"

**Symptoms:**
```
Failed to start MCP server: kansofy-trade
```

**Solutions:**

1. **Use full Python path:**
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "/Users/yourname/kansofy-trade/venv/bin/python",
      "args": ["/Users/yourname/kansofy-trade/mcp_server.py"]
    }
  }
}
```

2. **Add environment variables:**
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/kansofy-trade",
        "DATABASE_PATH": "/path/to/kansofy-trade/kansofy_trade.db"
      }
    }
  }
}
```

### Document Processing

#### Issue: Document upload fails

**Symptoms:**
- "File too large" error
- "Unsupported file type" error
- Upload hangs indefinitely

**Solutions:**

1. **Check file size:**
```python
import os
file_size = os.path.getsize("document.pdf") / (1024*1024)  # Size in MB
print(f"File size: {file_size:.2f} MB")
# Must be < 50MB
```

2. **Verify file format:**
```python
# Supported formats
SUPPORTED = ['.pdf', '.txt', '.csv', '.html', '.docx']

# Check extension
import os
_, ext = os.path.splitext("document.pdf")
if ext.lower() not in SUPPORTED:
    print(f"Unsupported format: {ext}")
```

3. **Check upload directory:**
```bash
# Ensure upload directory exists and is writable
ls -la uploads/
mkdir -p uploads
chmod 755 uploads/
```

4. **Test with simple file:**
```python
# Create test file
with open("test.txt", "w") as f:
    f.write("Test document content")

# Try uploading
result = upload_document(file_path="test.txt")
print(result)
```

#### Issue: Processing stuck at "processing" status

**Symptoms:**
- Document status remains "processing" indefinitely
- No error messages

**Solutions:**

1. **Check processing logs:**
```python
# Get document status
doc = get_document_details(document_id=42)
print(f"Status: {doc['status']}")
print(f"Uploaded: {doc['uploaded_at']}")
print(f"Processed: {doc['processed_at']}")

# Check processing logs
from app.models.document import DocumentProcessingLog
logs = session.query(DocumentProcessingLog).filter_by(document_id=42).all()
for log in logs:
    print(f"{log.event_type}: {log.event_data}")
```

2. **Manually trigger processing:**
```python
# Retry processing for stuck document
from app.services.document_processor import DocumentProcessor
processor = DocumentProcessor()
result = processor.process_document(document_id=42)
print(result)
```

3. **Reset document status:**
```sql
-- In SQLite
UPDATE documents 
SET status = 'uploaded' 
WHERE id = 42;

-- Then reprocess
process_pending_documents()
```

#### Issue: Table extraction not working

**Note**: This is Docling (rule-based), not AI. If tables aren't extracted, they don't match Docling's patterns.

**Symptoms:**
- Tables in PDF not extracted
- `tables` field is empty or null

**Solutions:**

1. **Verify Docling is working:**
```python
from docling.document_converter import DocumentConverter
converter = DocumentConverter()

# Test conversion
result = converter.convert("document_with_tables.pdf")
print(f"Tables found: {len(result.tables)}")
```

2. **Check table format:**
```python
# Get extracted tables
tables = get_document_tables(document_id=42, format="json")
print(f"Number of tables: {tables['tables_count']}")

# If 0, document might not have detectable tables
# Try manual extraction with different settings
```

### Search Issues

#### Issue: Search returns no results

**Symptoms:**
- Search returns empty results
- Known documents not found

**Solutions:**

1. **Verify FTS5 index:**
```python
# Check if documents are indexed
import sqlite3
conn = sqlite3.connect('kansofy_trade.db')
cursor = conn.execute("SELECT COUNT(*) FROM document_search")
print(f"Indexed documents: {cursor.fetchone()[0]}")

# Rebuild index if needed
cursor.execute("INSERT INTO document_search(document_search) VALUES('rebuild')")
conn.commit()
```

2. **Check document status:**
```python
# Only completed documents are searchable
stats = get_document_statistics()
print(f"Completed: {stats['status_breakdown']['completed']}")
print(f"Processing: {stats['status_breakdown']['processing']}")

# Process pending documents
if stats['status_breakdown']['uploaded'] > 0:
    process_pending_documents()
```

3. **Test with simple query:**
```python
# Start with single word
results = search_documents("invoice")

# If no results, check any documents exist
all_docs = search_documents("*")
print(f"Total searchable documents: {all_docs['results_count']}")
```

#### Issue: Vector search not working

**Note**: Vectors are pre-computed once. Search is pure math (cosine similarity), not AI.

**Symptoms:**
- `vector_search` returns no results
- "No embeddings found" error

**Solutions:**

1. **Generate embeddings:**
```python
# Update all embeddings
result = update_embeddings()
print(f"Updated: {result['documents_updated']} documents")

# Verify embeddings exist
import sqlite3
conn = sqlite3.connect('kansofy_trade.db')
cursor = conn.execute("SELECT COUNT(*) FROM document_embeddings")
print(f"Total embeddings: {cursor.fetchone()[0]}")
```

2. **Check model files:**
```bash
# Verify model is downloaded
ls -la model_cache/
# Should see model files (~50MB)

# Re-download if missing
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2')"
```

3. **Test embedding generation:**
```python
from app.core.vector_store import generate_embedding
embedding = generate_embedding("test text")
print(f"Embedding shape: {len(embedding)}")  # Should be 384
```

### Performance Problems

#### Issue: Slow document processing

**Symptoms:**
- Processing takes >10 seconds per document
- System becomes unresponsive

**Solutions:**

1. **Check system resources:**
```python
health = get_system_health(include_metrics=True)
print(f"CPU: {health['metrics']['cpu_usage_percent']}%")
print(f"Memory: {health['metrics']['memory_usage_mb']} MB")

# If high usage, restart server
```

2. **Optimize batch size:**
```python
# Process in smaller batches
import time

docs = get_pending_documents()
for batch in chunks(docs, 10):  # Process 10 at a time
    for doc in batch:
        process_document(doc)
    time.sleep(1)  # Brief pause between batches
```

3. **Clear old data:**
```sql
-- Remove old processing logs
DELETE FROM document_processing_logs 
WHERE created_at < date('now', '-30 days');

-- Vacuum database
VACUUM;
```

#### Issue: Search is slow

**Symptoms:**
- Search takes >1 second
- UI becomes unresponsive

**Solutions:**

1. **Optimize search queries:**
```python
# Instead of wildcard everything
slow = search_documents("*")

# Use specific terms
fast = search_documents("invoice 2024", limit=20)
```

2. **Rebuild FTS5 index:**
```sql
-- Rebuild search index
INSERT INTO document_search(document_search) VALUES('rebuild');
INSERT INTO document_search(document_search) VALUES('optimize');
```

3. **Increase cache size:**
```python
# In database.py
engine = create_engine(
    "sqlite:///kansofy_trade.db",
    connect_args={"check_same_thread": False},
    pool_size=20,  # Increase pool
    echo=False  # Disable query logging
)
```

## Debug Commands

### Diagnostic Scripts

```python
# diagnose.py - Run complete diagnostics
import asyncio
from app.core.database import get_db_context
from app.core.config import get_settings

async def diagnose():
    print("🔍 Running Diagnostics...")
    
    # 1. Check database
    try:
        async with get_db_context() as db:
            result = await db.execute("SELECT COUNT(*) FROM documents")
            count = result.scalar()
            print(f"✅ Database connected: {count} documents")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 2. Check file system
    import os
    if os.path.exists("uploads"):
        files = len(os.listdir("uploads"))
        print(f"✅ Upload directory: {files} files")
    else:
        print("❌ Upload directory missing")
    
    # 3. Check search index
    try:
        from app.core.database import search_documents_fts5
        results = await search_documents_fts5("test", limit=1)
        print(f"✅ FTS5 search working")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # 4. Check vector store
    try:
        from app.core.vector_store import init_vector_store
        init_vector_store()
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"❌ Vector store error: {e}")
    
    # 5. Check MCP server
    try:
        import mcp.server
        print("✅ MCP module loaded")
    except ImportError:
        print("❌ MCP module not found")

asyncio.run(diagnose())
```

### Database Inspection

```sql
-- Check database integrity
PRAGMA integrity_check;

-- View table sizes
SELECT 
    name as table_name,
    COUNT(*) as row_count
FROM sqlite_master 
WHERE type='table'
GROUP BY name;

-- Check processing queue
SELECT 
    status, 
    COUNT(*) as count 
FROM documents 
GROUP BY status;

-- Recent errors
SELECT * FROM document_processing_logs 
WHERE event_type = 'error' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Performance Profiling

```python
# profile_search.py - Profile search performance
import time
import statistics

def profile_search(queries, iterations=10):
    times = []
    
    for query in queries:
        query_times = []
        for _ in range(iterations):
            start = time.time()
            results = search_documents(query)
            elapsed = time.time() - start
            query_times.append(elapsed)
        
        avg_time = statistics.mean(query_times)
        print(f"Query: '{query}'")
        print(f"  Avg time: {avg_time:.3f}s")
        print(f"  Min/Max: {min(query_times):.3f}s / {max(query_times):.3f}s")
        times.extend(query_times)
    
    print(f"\nOverall average: {statistics.mean(times):.3f}s")

# Test with various queries
profile_search([
    "invoice",
    "contract AND arbitration",
    '"payment terms"',
    "ship*"
])
```

## Error Messages

### Common Error Messages and Solutions

#### "Tool execution failed: Database is locked"

**Cause**: SQLite database is being accessed by multiple processes

**Solution:**
```python
# Use connection pooling
from sqlalchemy.pool import StaticPool
engine = create_engine(
    "sqlite:///kansofy_trade.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
```

#### "ValueError: Document not found"

**Cause**: Trying to access non-existent document

**Solution:**
```python
# Check document exists first
try:
    doc = get_document_details(document_id=999)
except ValueError as e:
    print(f"Document not found: {e}")
    # Handle missing document
```

#### "ProcessingError: Failed to extract text"

**Cause**: Corrupted or encrypted PDF

**Solution:**
```python
# Check if PDF is encrypted
import PyPDF2

with open("document.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    if reader.is_encrypted:
        print("PDF is encrypted")
        # Try decrypting or request unencrypted version
```

#### "MemoryError: Unable to allocate array"

**Cause**: Large document or insufficient memory

**Solution:**
```python
# Process large documents in chunks
def process_large_document(file_path):
    # Split into smaller chunks
    chunk_size = 1000  # Characters per chunk
    
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            # Process chunk
            process_chunk(chunk)
```

## FAQ

### General Questions

**Q: How many documents can Kansofy-Trade handle?**
A: The system is tested with up to 100,000 documents. Performance depends on document size and complexity. For larger collections, consider PostgreSQL migration.

**Q: Can I use this without Claude Desktop?**
A: Yes! Works with any MCP client (Claude, Copilot, etc.) or standalone via REST API.

**Q: What file formats are supported?**
A: PDF, TXT, CSV, HTML, and DOCX. PDF is the primary format with best support for tables and formatting.

**Q: How accurate is the extraction?**
A: Docling is deterministic - same document always gives same result. No AI variability. Accuracy depends on how well documents match Docling's rules.

**Q: Can it handle scanned PDFs?**
A: No. Scanned PDFs need OCR (AI/ML). This engine is deterministic - no AI required.

### Technical Questions

**Q: Why SQLite instead of PostgreSQL?**
A: SQLite provides excellent performance for single-user scenarios, requires no setup, and includes FTS5 for full-text search. PostgreSQL migration path is available for scaling.

**Q: How are embeddings generated?**
A: Pre-computed once using all-MiniLM-L6-v2. Search is then pure math (cosine similarity) - no AI inference at search time.

**Q: Is my data secure?**
A: 100% local, zero external dependencies. No AI APIs, no cloud services. Everything runs on your machine.

**Q: Can I customize the extraction?**
A: Yes, you can modify `app/services/document_processor.py` to add custom extraction logic for specific document types.

**Q: How do I backup my data?**
A: Copy the `kansofy_trade.db` file and `uploads/` directory. These contain all your data.

### Integration Questions

**Q: Can I integrate with my existing system?**
A: Yes, use the REST API endpoints. See the [API documentation](MCP_TOOLS_REFERENCE.md) for details.

**Q: Is there a Python client library?**
A: The MCP tools can be called directly from Python. See [Usage Guide](USAGE_GUIDE.md) for examples.

**Q: Can multiple users access the system?**
A: Currently single-user focused. Multi-user support with authentication is on the roadmap.

**Q: How do I deploy to production?**
A: See the Docker deployment section in [Installation Guide](INSTALLATION.md). Use PostgreSQL for production deployments.

## Advanced Debugging

### Enable Debug Logging

```python
# In app/core/logging_config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Set specific loggers
logging.getLogger('app.services.document_processor').setLevel(logging.DEBUG)
logging.getLogger('app.core.vector_store').setLevel(logging.DEBUG)
```

### Database Query Logging

```python
# Enable SQL query logging
engine = create_engine(
    "sqlite:///kansofy_trade.db",
    echo=True  # Print all SQL queries
)

# Or log to file
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Memory Profiling

```python
# Install memory_profiler: pip install memory_profiler

from memory_profiler import profile

@profile
def process_large_document(file_path):
    # Your processing code
    pass

# Run with: python -m memory_profiler your_script.py
```

### Network Debugging (MCP)

```bash
# Monitor MCP communication
# On macOS
sudo tcpdump -i lo0 -A 'port 5000'

# Check if MCP server is listening
lsof -i :5000
netstat -an | grep 5000
```

## Getting Help

### Before Asking for Help

1. **Check this guide** - Most issues are covered here
2. **Read error messages** - They often indicate the solution
3. **Try the diagnostic script** - Run `python diagnose.py`
4. **Check logs** - Look in `debug.log` and Claude Desktop logs
5. **Test with simple examples** - Isolate the problem

### How to Report Issues

When reporting issues, include:

```markdown
## Environment
- OS: [e.g., macOS 14.1]
- Python version: [e.g., 3.9.7]
- Kansofy-Trade version: [e.g., 1.0.0]
- Claude Desktop version: [if applicable]

## Issue Description
[Clear description of the problem]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [etc.]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Messages
```
[Paste complete error messages]
```

## Attempted Solutions
[What you've already tried]

## Additional Context
[Any other relevant information]
```

### Support Channels

- **GitHub Issues**: [github.com/kansofy/kansofy-trade/issues](https://github.com/kansofy/kansofy-trade/issues)
- **Discussions**: [github.com/kansofy/kansofy-trade/discussions](https://github.com/kansofy/kansofy-trade/discussions)
- **Documentation**: [Full documentation](README.md)

### Quick Support Checklist

- [ ] Virtual environment activated
- [ ] All requirements installed
- [ ] Database initialized
- [ ] Upload directory exists and writable
- [ ] Claude Desktop restarted
- [ ] Config file syntax valid
- [ ] Absolute paths in config
- [ ] No other processes using database
- [ ] Sufficient disk space
- [ ] Proper file permissions

---

*Still stuck? [Open an issue](https://github.com/kansofy/kansofy-trade/issues/new) with details from the diagnostic script.*