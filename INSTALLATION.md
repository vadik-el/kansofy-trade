# Zero-Dependency Installation 📦

**No AI required. No API keys. No cloud services. Just install and run.**

This engine runs 100% locally with zero external dependencies.

## Table of Contents
- [What You DON'T Need](#what-you-dont-need)
- [System Requirements](#system-requirements)
- [Quick Install (5 minutes)](#quick-install-5-minutes)
- [Detailed Installation](#detailed-installation)
- [Claude Desktop Configuration](#claude-desktop-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Docker Installation](#docker-installation)
- [Development Setup](#development-setup)

## What You DON'T Need

❌ **No AI Dependencies:**
- No OpenAI API keys
- No Anthropic API keys
- No cloud AI services
- No GPU required
- No CUDA/ML frameworks
- No model training
- No inference servers

✅ **What You DO Need:**
- Python 3.9+ (standard installation)
- 4GB RAM (for document processing)
- Any MCP-compatible client (Claude Desktop, Copilot Studio, etc.)

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 500MB for application + space for documents
- **OS**: macOS, Linux, Windows 10/11

### Software Dependencies
- Python 3.9+
- pip (Python package manager)
- Git
- Any MCP client (Claude Desktop, Microsoft Copilot, or others)

### Checking Your System
```bash
# Check Python version
python --version  # Should show 3.9 or higher

# Check pip
pip --version

# Check git
git --version

# Check available disk space
df -h  # Linux/Mac
# or
dir  # Windows
```

## Quick Install (5 minutes)

For experienced users who want to get started immediately:

```bash
# 1. Clone repository
git clone https://github.com/kansofy/kansofy-trade.git
cd kansofy-trade

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database (SQLite, no external DB needed)
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 5. Configure your MCP client (Claude, Copilot, etc.)

# 6. Test installation
python test_mcp_direct.py
```

## Detailed Installation

### Step 1: Clone the Repository

```bash
# Using HTTPS (recommended)
git clone https://github.com/kansofy/kansofy-trade.git

# Or using SSH (if you have SSH keys set up)
git clone git@github.com:kansofy/kansofy-trade.git

# Navigate to the project directory
cd kansofy-trade
```

### Step 2: Set Up Python Environment

**Option A: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**Option B: Conda Environment**
```bash
# Create conda environment
conda create -n kansofy-trade python=3.9

# Activate environment
conda activate kansofy-trade
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify key packages installed (all deterministic, no AI)
python -c "import mcp.server; print('✅ MCP Protocol installed')"
python -c "import docling; print('✅ Docling (rule-based parser) installed')"
python -c "import fastapi; print('✅ FastAPI (web framework) installed')"
python -c "import sentence_transformers; print('✅ Embeddings (one-time computation) installed')"
```

**Troubleshooting Package Installation:**
```bash
# If you encounter SSL errors
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# If you encounter permission errors
pip install --user -r requirements.txt

# For specific package issues
pip install mcp --no-cache-dir
pip install docling --no-cache-dir
```

### Step 4: Initialize the Database

```bash
# Run database initialization
python << EOF
import asyncio
from app.core.database import init_database

async def setup():
    await init_database()
    print("✅ Database initialized successfully")

asyncio.run(setup())
EOF

# Verify database created
ls -la kansofy_trade.db  # Should see the database file
```

### Step 5: Pre-compute Embeddings Model (One-Time)

**Note**: This downloads a small model for one-time vector computation. No AI inference happens at search time - vectors are pre-computed and stored.

```bash
python << EOF
from sentence_transformers import SentenceTransformer
print("Downloading embedding model for one-time vector computation...")
print("This is NOT for AI inference - just pre-computing document vectors")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Embedding model ready (vectors are pre-computed, no AI at search time)")
EOF
```

## MCP Client Configuration

### Option A: Claude Desktop (Anthropic)

#### macOS Configuration

1. **Locate Claude Desktop Config**:
```bash
# Config file location
~/Library/Application Support/Claude/claude_desktop_config.json

# Create directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude
```

2. **Edit Configuration**:
```bash
# Open in your preferred editor
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. **Add Kansofy-Trade Server**:
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["/absolute/path/to/kansofy-trade/mcp_server.py"],
      "env": {
        "DATABASE_PATH": "/absolute/path/to/kansofy-trade/kansofy_trade.db"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to` with your actual path:
```bash
# Get the absolute path
pwd  # Run this in the kansofy-trade directory
```

#### Windows Configuration

1. **Locate Config File**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

2. **Edit with Notepad**:
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

3. **Add Configuration** (use forward slashes or escaped backslashes):
```json
{
  "mcpServers": {
    "kansofy-trade": {
      "command": "python",
      "args": ["C:/path/to/kansofy-trade/mcp_server.py"],
      "env": {
        "DATABASE_PATH": "C:/path/to/kansofy-trade/kansofy_trade.db"
      }
    }
  }
}
```

#### Linux Configuration

1. **Locate Config**:
```bash
~/.config/Claude/claude_desktop_config.json
```

2. **Create and Edit**:
```bash
mkdir -p ~/.config/Claude
nano ~/.config/Claude/claude_desktop_config.json
```

3. **Add Configuration** (same as macOS format)

## Verification

### Step 1: Test MCP Server Directly

```bash
# Run the test script
python test_mcp_direct.py

# Expected output:
# ✅ Engine started successfully (no AI required)
# ✅ Operations available: 14 deterministic operations
# ✅ SQL search test passed (no AI)
# ✅ Health check passed
```

### Step 2: Test Web Interface

```bash
# Start the web server
python -m uvicorn app.main:app --reload --port 8000

# Open in browser
# http://localhost:8000

# You should see the upload interface
```

### Option B: Microsoft Copilot Studio

```json
// Configure in Copilot Studio as external tool
{
  "tool": {
    "name": "kansofy-trade",
    "type": "mcp",
    "endpoint": "http://localhost:5000",
    "description": "Document workflow engine"
  }
}
```

### Option C: Any MCP-Compatible Client

```bash
# Start the MCP server
python mcp_server.py

# Server listens on default MCP port
# Configure your client to connect to this endpoint
```

### Step 3: Test MCP Client Integration

1. **Restart your MCP client** completely (Quit and reopen)

2. **Check MCP Connection** in your AI assistant:
```
What MCP tools do you have available?
```

Your AI should list the 14 Kansofy-Trade engine operations.

3. **Test an Operation**:
```
Can you check the health of the document engine?
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" Errors

```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 2. MCP Client Not Finding Engine

**Check config syntax**:
```bash
# Validate JSON syntax
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Check path is absolute**:
```bash
# This WON'T work
"args": ["./mcp_server.py"]  # Relative path

# This WILL work
"args": ["/Users/yourname/kansofy-trade/mcp_server.py"]  # Absolute path
```

**Check Python path**:
```bash
# Get Python executable path
which python

# Update config to use full path
"command": "/Users/yourname/kansofy-trade/venv/bin/python"
```

#### 3. Database Errors

```bash
# Reset database
rm kansofy_trade.db
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

#### 4. Permission Denied

```bash
# Make scripts executable
chmod +x mcp_server.py
chmod +x run_tests.sh

# Fix upload directory permissions
chmod 755 uploads/
```

#### 5. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python -m uvicorn app.main:app --port 8001
```

### Diagnostic Commands

```bash
# Check all dependencies installed
pip list | grep -E "mcp|docling|fastapi|sentence-transformers"

# Test database connection
python -c "import sqlite3; conn = sqlite3.connect('kansofy_trade.db'); print('✅ Database accessible')"

# Test MCP server can start
python mcp_server.py --help

# Check MCP client logs
# Claude Desktop (macOS):
tail -f ~/Library/Logs/Claude/mcp.log
# Other clients: check respective log locations
```

## Docker Installation

For isolated, reproducible installations:

```bash
# Build Docker image
docker build -t kansofy-trade .

# Run container
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads kansofy-trade

# For MCP with Docker
docker run -it kansofy-trade python mcp_server.py
```

**Docker Compose** (recommended for production):
```yaml
# docker-compose.yml included in repository
docker-compose up -d
```

## Development Setup

For contributors and developers:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run with hot reload
python -m uvicorn app.main:app --reload --port 8000

# Format code
black app/ tests/
isort app/ tests/
```

### Environment Variables

Create `.env` file for development:
```bash
# .env
DEBUG=true
DATABASE_PATH=./kansofy_trade.db  # Local SQLite, no external DB
UPLOAD_DIR=./uploads              # Local storage, no cloud
LOG_LEVEL=DEBUG
MAX_UPLOAD_SIZE=52428800          # 50MB
# Note: No API keys needed!
```

## Next Steps

✅ Installation complete! Now you can:

1. **Read the [Usage Guide](USAGE_GUIDE.md)** for tutorials
2. **Explore [MCP Tools Reference](MCP_TOOLS_REFERENCE.md)** for all available tools
3. **Upload your first document** via the web interface
4. **Start using with any MCP client** (Claude, Copilot, etc.) for document workflows

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/kansofy/kansofy-trade/issues)
- **Documentation**: [Full Documentation](README.md)
- **Community**: [Discussions](https://github.com/kansofy/kansofy-trade/discussions)

---

*Installation trouble? [Check our FAQ](TROUBLESHOOTING.md) or [open an issue](https://github.com/kansofy/kansofy-trade/issues/new)*