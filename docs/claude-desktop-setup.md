# Claude Desktop Integration Guide

This guide shows you how to integrate Kansofy-Trade with Claude Desktop for seamless document intelligence.

## Quick Setup

### 1. Install Dependencies

```bash
cd kansofy-trade
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python -m app.core.database
# Or start the web server once to auto-initialize
python -m uvicorn app.main:app --reload
```

### 3. Configure Claude Desktop

Copy the MCP server configuration to your Claude Desktop config:

**Location of Claude Desktop config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/your/kansofy-trade",
      "env": {
        "DATABASE_PATH": "./kansofy_trade.db",
        "UPLOAD_DIR": "./uploads"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/kansofy-trade` with the actual path to your Kansofy-Trade installation.

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

### 5. Verify Connection

In Claude Desktop, try these commands:

```
Can you check the Kansofy-Trade system health?
```

```
Search for documents containing "invoice"
```

## Available MCP Tools

Once connected, Claude Desktop can use these tools:

### 🔍 `search_documents`
Search documents using full-text search with FTS5
- Supports boolean operators: `copper AND invoice`
- Phrase matching: `"purchase order"`
- Wildcards: `ship*`

### 📄 `get_document_details`
Get detailed information about specific documents
- Document metadata and processing status
- Extracted entities (amounts, dates, companies)
- Content preview and confidence scores

### 📊 `get_document_statistics`
Get comprehensive document collection statistics
- Total documents, file sizes, processing status
- Breakdown by file types and recent activity
- Performance and quality metrics

### 🔍 `analyze_document_content`
Analyze document content for patterns and insights
- Entity extraction and pattern analysis
- Content summarization and key insights
- Cross-document relationship analysis

### 🏥 `get_system_health`
Check system health and performance
- Database connectivity and search index status
- Processing queue status and disk usage
- Performance metrics and configuration info

## Example Conversations

### Document Search
```
User: "Find all documents related to copper purchases"
Claude: I'll search for documents containing "copper" and "purchase" terms.
[Uses search_documents tool with query "copper purchase"]
```

### Document Analysis
```
User: "What are the key entities in document ID 123?"
Claude: Let me analyze that document for you.
[Uses get_document_details and analyze_document_content tools]
```

### System Monitoring
```
User: "How is the document processing system performing?"
Claude: I'll check the system health and statistics.
[Uses get_system_health and get_document_statistics tools]
```

## Troubleshooting

### MCP Server Not Starting
1. Check Python path and dependencies
2. Verify database file permissions
3. Ensure upload directory exists

### No Search Results
1. Upload and process some documents first
2. Check document processing status
3. Verify FTS5 search index is built

### Permission Errors
1. Check file permissions on database and upload directories
2. Ensure Python can write to the project directory
3. Run with appropriate user permissions

## Advanced Configuration

### Custom Database Location
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/kansofy-trade",
      "env": {
        "DATABASE_PATH": "/custom/path/documents.db",
        "UPLOAD_DIR": "/custom/uploads"
      }
    }
  }
}
```

### Debug Mode
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/kansofy-trade",
      "env": {
        "DATABASE_PATH": "./kansofy_trade.db",
        "UPLOAD_DIR": "./uploads",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Security Notes

- Kansofy-Trade runs locally and doesn't send data to external services
- All document processing happens on your machine
- Database and uploaded files stay in your local filesystem
- No API keys or cloud services required for basic functionality