# Installation Guide 📦

Complete setup guide for Kansofy-Trade MCP Server with Claude Desktop integration.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Install (5 minutes)](#quick-install-5-minutes)
- [Detailed Installation](#detailed-installation)
- [Claude Desktop Configuration](#claude-desktop-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Docker Installation](#docker-installation)
- [Development Setup](#development-setup)

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
- Claude Desktop (for MCP integration)

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

# 4. Initialize database
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 5. Configure Claude Desktop (see below)

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

# Verify key packages installed
python -c "import mcp.server; print('✅ MCP installed')"
python -c "import docling; print('✅ Docling installed')"
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import sentence_transformers; print('✅ Sentence Transformers installed')"
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

### Step 5: Download Model Files (First Run)

The sentence transformer model will be downloaded automatically on first use. To pre-download:

```bash
python << EOF
from sentence_transformers import SentenceTransformer
print("Downloading model... this may take a minute")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model downloaded successfully")
EOF
```

## Claude Desktop Configuration

### macOS Configuration

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

### Windows Configuration

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

### Linux Configuration

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
# ✅ MCP Server started successfully
# ✅ Tools listed: 14 tools available
# ✅ Search test passed
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

### Step 3: Test Claude Desktop Integration

1. **Restart Claude Desktop** completely (Quit and reopen)

2. **Check MCP Connection** in Claude:
```
What MCP tools do you have available?
```

Claude should list the 14 Kansofy-Trade tools.

3. **Test a Tool**:
```
Can you check the health of the Kansofy-Trade system?
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

#### 2. Claude Desktop Not Finding MCP Server

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

# Check Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/mcp.log
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
DATABASE_PATH=./kansofy_trade.db
UPLOAD_DIR=./uploads
LOG_LEVEL=DEBUG
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## Next Steps

✅ Installation complete! Now you can:

1. **Read the [Usage Guide](USAGE_GUIDE.md)** for tutorials
2. **Explore [MCP Tools Reference](MCP_TOOLS_REFERENCE.md)** for all available tools
3. **Upload your first document** via the web interface
4. **Start using with Claude Desktop** for intelligent document analysis

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/kansofy/kansofy-trade/issues)
- **Documentation**: [Full Documentation](README.md)
- **Community**: [Discussions](https://github.com/kansofy/kansofy-trade/discussions)

---

*Installation trouble? [Check our FAQ](TROUBLESHOOTING.md) or [open an issue](https://github.com/kansofy/kansofy-trade/issues/new)*