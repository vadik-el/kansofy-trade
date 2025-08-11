#!/usr/bin/env python3
"""Test document upload via MCP tool"""

import asyncio
from mcp_server import handle_call_tool
from pathlib import Path

async def test_upload():
    """Test the upload_document tool"""
    
    print("=" * 60)
    print("Testing Document Upload Tool")
    print("=" * 60)
    
    # Create a test document
    test_file = Path("test_document.txt")
    test_content = """
    This is a test document for the Kansofy-Trade system.
    
    It contains some sample text that can be used to test:
    - Document upload functionality
    - Text extraction
    - Search capabilities
    - Duplicate detection
    
    Test date: 2024-01-15
    Category: Test Document
    """
    
    test_file.write_text(test_content)
    print(f"\n✅ Created test file: {test_file}")
    
    # Test 1: Upload with file_path
    print("\n1. Testing upload with file_path...")
    try:
        result = await handle_call_tool("upload_document", {
            "file_path": str(test_file),
            "category": "report",
            "process_immediately": False
        })
        if result and len(result) > 0:
            print(result[0].text)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Check system statistics after upload
    print("\n2. Checking system statistics...")
    try:
        result = await handle_call_tool("get_document_statistics", {})
        if result and len(result) > 0:
            print(result[0].text)
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
    
    # Clean up
    test_file.unlink()
    print(f"\n🧹 Cleaned up test file")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_upload())