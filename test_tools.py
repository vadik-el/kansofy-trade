#!/usr/bin/env python3
"""Test MCP tools creation"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.types import Tool, ListToolsResult

# Import the TOOLS from mcp_server
from mcp_server import TOOLS

print(f"Number of tools: {len(TOOLS)}")
print(f"Type of TOOLS: {type(TOOLS)}")
print(f"Type of first item: {type(TOOLS[0])}")

for i, tool in enumerate(TOOLS):
    print(f"Tool {i+1}: {tool.name if hasattr(tool, 'name') else 'NO NAME'} - Type: {type(tool)}")
    
# Test creating ListToolsResult
try:
    result = ListToolsResult(tools=TOOLS)
    print("\n✅ ListToolsResult created successfully!")
    print(f"Number of tools in result: {len(result.tools)}")
except Exception as e:
    print(f"\n❌ Error creating ListToolsResult: {e}")
    import traceback
    traceback.print_exc()