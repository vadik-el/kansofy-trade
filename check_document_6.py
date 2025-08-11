#!/usr/bin/env python3
"""Check status of document 6 and attempt to process it"""

import asyncio
from mcp_server import handle_call_tool

async def check_and_process():
    """Check document 6 status and process if needed"""
    
    print("=" * 60)
    print("Checking Document ID 6 (VEL_CV.pdf)")
    print("=" * 60)
    
    # Check document details
    print("\n1. Getting document details...")
    result = await handle_call_tool("get_document_details", {"document_id": 6})
    if result and len(result) > 0:
        print(result[0].text)
    
    # Try to process it using update_embeddings
    print("\n2. Attempting to process the document...")
    result = await handle_call_tool("update_embeddings", {})
    if result and len(result) > 0:
        print(result[0].text)
    
    # Check status again
    print("\n3. Checking updated status...")
    result = await handle_call_tool("get_document_details", {"document_id": 6})
    if result and len(result) > 0:
        # Extract just the status line
        lines = result[0].text.split('\n')
        for line in lines:
            if 'Status:' in line or 'status' in line.lower():
                print(line)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_and_process())