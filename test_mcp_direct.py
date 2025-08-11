#!/usr/bin/env python3
"""Test MCP server directly"""

import asyncio
import json
from mcp_server import server, handle_list_tools, handle_call_tool


async def test_mcp_server():
    """Test the MCP server functions directly"""
    
    print("=" * 60)
    print("Testing MCP Server Functions")
    print("=" * 60)
    
    # Test 1: List tools
    print("\n1. Testing list_tools handler...")
    try:
        tools = await handle_list_tools()
        print(f"✅ Listed {len(tools)} tools")
        print(f"   Tool names: {[t.name for t in tools]}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Call a simple tool (get_system_health)
    print("\n2. Testing get_system_health tool...")
    try:
        # Call the handler directly
        result = await handle_call_tool("get_system_health", {})
        print(f"✅ Tool returned: {type(result)}")
        if isinstance(result, list) and len(result) > 0:
            print(f"   Content type: {result[0].type if hasattr(result[0], 'type') else 'unknown'}")
            print(f"   Content preview: {result[0].text[:100] if hasattr(result[0], 'text') else 'N/A'}...")
    except Exception as e:
        print(f"❌ Error calling tool: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Call a tool with arguments (search_documents)
    print("\n3. Testing search_documents tool...")
    try:
        # Call the handler directly
        result = await handle_call_tool("search_documents", {"query": "test", "limit": 5})
        print(f"✅ Tool returned: {type(result)}")
        if isinstance(result, list) and len(result) > 0:
            print(f"   Content type: {result[0].type if hasattr(result[0], 'type') else 'unknown'}")
            print(f"   Response length: {len(result[0].text) if hasattr(result[0], 'text') else 0} chars")
    except Exception as e:
        print(f"❌ Error calling tool: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())