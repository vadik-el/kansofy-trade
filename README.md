<div align="center">
  <img src="logo.svg" alt="Kansofy-Trade Logo" width="200" />
  
  # TradeMCP
  
  **Open-source MCP server for document workflow simplification.**
</div>

--- Built on IBM's [Docling](https://github.com/DS4SD/docling) for powerful document extraction.

## 🚀 Works Out of the Box

**No AI needed for document processing. No API keys. No cloud dependencies. Works with any AI platform.**

This MCP server runs 100% locally using Docling for document extraction - no AI required for the actual processing. Connect it to any MCP-compatible AI assistant:
- **Claude Desktop** by Anthropic
- **Microsoft Copilot** via Copilot Studio  
- **Any MCP-compatible client** (growing ecosystem)

## 🔌 Vendor & Model Agnostic

**One engine, any AI platform.**

The Model Context Protocol (MCP) is an open standard. This means:
- ✅ Not locked to Anthropic or Claude
- ✅ Works with Microsoft Copilot Studio
- ✅ Compatible with any MCP implementation
- ✅ Future-proof as more platforms adopt MCP
- ✅ Use with GPT, Gemini, Llama, or any model

Your document infrastructure shouldn't depend on a single AI vendor. Kansofy-Trade ensures it doesn't.

## 🏗️ The Engine, Not the Brain

Kansofy-Trade is the **engine** that enables document operations:
- **Powered by Docling**: IBM Research's document parser (no AI needed)
- **Deterministic Processing**: Same document = same output every time
- **MCP Native**: Works with any MCP-compatible client
- **Zero Configuration**: Install and run — no setup required
- **100% Local**: Your documents never leave your machine

The **brain** (workflow intelligence, trade expertise, compliance logic) can come from any AI model or commercial solution - but the engine runs without any AI.

## 📚 Built on Open Standards

### Docling by IBM Research
This project leverages [Docling](https://github.com/DS4SD/docling), IBM's advanced document conversion technology:
- **Rule-based extraction** - No AI/ML required
- Extracts text, tables, and structure from PDFs, DOCX, XLSX, PPTX, and more
- Maintains document layout and formatting intelligence  
- Handles complex multi-column layouts and embedded tables
- Open-source (MIT licensed) and actively maintained

### Model Context Protocol (MCP)
Open standard for AI-tool communication:
- Works with Claude Desktop (Anthropic)
- Compatible with Copilot Studio (Microsoft)
- Supports any MCP client implementation
- Vendor-neutral protocol specification

## 🎯 What This Is (And Isn't)

**This IS:**
- ✅ A vendor-agnostic MCP server with 14 document tools
- ✅ Deterministic document extraction via Docling (no AI)
- ✅ Full-text and semantic search capabilities
- ✅ Production-ready document processing engine
- ✅ 100% local, offline-capable, no external dependencies

**This IS NOT:**
- ❌ An AI-powered document processor (it's deterministic)
- ❌ Tied to any specific AI vendor
- ❌ An AI model (it's infrastructure for any AI)
- ❌ A complete workflow automation solution
- ❌ The commercial Kansofy product

## ⚡ Quick Start

### With Claude Desktop
```bash
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["/path/to/kansofy-trade/mcp_server.py"]
    }
  }
}
```

### With Microsoft Copilot Studio
```bash
# Configure in Copilot Studio as external tool
# Point to the MCP server endpoint
# Use the standard MCP protocol
```

### With Any MCP Client
```bash
# Start the MCP server
python mcp_server.py

# Connect any MCP-compatible client
# Server speaks standard MCP protocol
```

## 🛠️ What You Get

### Document Processing (No AI Required)
```python
# Docling extracts everything deterministically
upload_document("complex_invoice.pdf")
# ✓ Text extracted (rule-based)
# ✓ Tables preserved (pattern matching)
# ✓ Structure maintained (document parsing)
# ✓ Same input = same output every time
```

### Intelligent Search (Still No AI)
```python
# Full-text search with SQLite FTS5
search_documents("payment terms net 30")

# Semantic similarity with pre-computed embeddings
vector_search("documents about shipping delays")

# Find duplicates using hashing
find_duplicates()
```

### MCP Tools for Any AI Assistant
All 14 tools work instantly with any MCP client:
- `upload_document` - Process any document format (no AI)
- `search_documents` - Lightning-fast full-text search (SQL)
- `vector_search` - Find similar documents (embeddings)
- `get_document_tables` - Extract tables from PDFs (Docling)
- [... and 10 more tools]

## 🧠 The Brain Lives Elsewhere

This engine provides the **infrastructure** (no AI). The **intelligence** comes from:

### Your AI Assistant (Claude, Copilot, etc.)
The AI provides the intelligence to:
- Understand your intent
- Orchestrate document operations
- Make decisions based on content
- Generate insights and summaries

### Your Own Implementation
Build your own workflows on top:
- Custom document classification
- Business rule validation
- Workflow orchestration
- Integration patterns

### Commercial Solutions
Production-ready intelligence:
- **Kansofy Trade Cloud**: Full SaaS with trade workflows
- **Kansofy Enterprise**: Self-hosted with compliance engine
- **Professional Services**: Custom workflow development

## 📊 How It Works Without AI

### Document Processing Pipeline
```
PDF/DOCX → Docling (rule-based) → Structured Data → SQLite
         ↓
    No AI needed
    Deterministic
    100% reproducible
```

### Search Pipeline
```
Query → FTS5 (SQL) → Results
      → Embeddings (pre-computed) → Similarity
      
No AI inference at search time
```

## 🌐 Platform Compatibility

| Platform | Status | Configuration |
|----------|--------|---------------|
| Claude Desktop | ✅ Tested | Native support |
| Microsoft Copilot | ✅ Compatible | Via Copilot Studio |
| OpenAI GPTs | 🔄 Planned | MCP bridge needed |
| Google Gemini | 🔄 Planned | MCP adapter |
| Open Source LLMs | ✅ Ready | Any MCP client |

## 🤝 Why This Architecture Matters

**No AI in the Engine Means:**
- Deterministic results (same input = same output)
- No API costs for document processing
- Works offline completely
- No rate limits or quotas
- Full data privacy (nothing leaves your machine)
- Predictable performance

**Any AI for the Brain Means:**
- Choose your preferred AI assistant
- Switch providers without changing infrastructure
- Use multiple AIs for different tasks
- Future-proof as AI landscape evolves

## 📈 When You Need More

You'll know it's time for commercial when:
- [ ] Processing >100 documents daily
- [ ] Need trade-specific workflows
- [ ] Require compliance validation
- [ ] Want pre-built intelligence
- [ ] ROI justifies enterprise features

## 🔗 Technical Foundation

- **Document Processing**: [Docling](https://github.com/DS4SD/docling) by IBM Research (no AI)
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.io) (open standard)
- **Search**: SQLite with FTS5 extension (deterministic SQL)
- **Embeddings**: Sentence-transformers (pre-computed, no inference)
- **Server**: FastAPI + Python 3.9+ (standard web framework)

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Installation](INSTALLATION.md) | Complete setup guide |
| [MCP Tools](MCP_TOOLS_REFERENCE.md) | All 14 tools documented |
| [Architecture](ARCHITECTURE.md) | System design & components |
| [Usage Guide](USAGE_GUIDE.md) | Examples and workflows |
| [Platform Compatibility](PLATFORM_COMPATIBILITY.md) | Multi-platform setup |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| [Contributing](CONTRIBUTING.md) | How to contribute |

## 🙏 Acknowledgements

- [IBM Research](https://github.com/DS4SD) for Docling
- [Anthropic](https://anthropic.com) for MCP protocol
- The open-source community

---

Built with ❤️ for the humans running global trade.  
The engine for document workflows. The foundation for agentic AI in trade.
