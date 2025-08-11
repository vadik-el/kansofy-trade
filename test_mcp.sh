#!/bin/bash

# Test script for Kansofy-Trade MCP Server

echo "🚀 Testing Kansofy-Trade MCP Server..."
echo ""

# 1. Check if database exists
if [ -f "kansofy_trade.db" ]; then
    echo "✅ Database exists"
else
    echo "❌ Database not found - initializing..."
    python3 -c "import asyncio; from app.core.database import init_database; asyncio.run(init_database())"
fi

# 2. Test MCP server startup
echo ""
echo "📡 Starting MCP server test..."
timeout 5 python3 mcp_server.py 2>&1 | head -20

echo ""
echo "✅ MCP server startup test complete"
echo ""
echo "To use with Claude Desktop, add this to your Claude Desktop config:"
echo ""
echo "~/.claude/claude_desktop_config.json:"
echo "{"
echo '  "mcpServers": {'
echo '    "kansofy-trade": {'
echo '      "command": "python3",'
echo '      "args": ["'$(pwd)'/mcp_server.py"],'
echo '      "env": {'
echo '        "PYTHONPATH": "'$(pwd)'"'
echo '      }'
echo '    }'
echo '  }'
echo "}"