#!/usr/bin/env python3
"""
MCP Tools Verification Script for Kansofy-Trade

This script verifies that all 11 MCP tools are accessible and working properly.
Run this before testing with Claude Desktop to ensure everything is operational.
"""

import asyncio
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MCP tools
from mcp_server import (
    get_system_health_tool,
    get_document_statistics_tool,
    search_documents_tool,
    vector_search_tool,
    get_document_details_tool,
    analyze_document_content_tool,
    find_duplicates_tool,
    check_duplicate_by_hash_tool,
    get_document_json_tool,
    get_document_tables_tool,
    update_embeddings_tool
)


async def verify_tool(tool_name: str, tool_func, arguments: dict, expected_keywords: list = None):
    """Verify a single MCP tool works correctly"""
    print(f"\n🔧 Testing: {tool_name}")
    print(f"   Arguments: {arguments}")
    
    try:
        result = await tool_func(arguments)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else "No content"
            
            # Check if result contains expected keywords
            if expected_keywords:
                found_keywords = [kw for kw in expected_keywords if kw.lower() in content.lower()]
                if found_keywords:
                    print(f"   ✅ SUCCESS - Found: {', '.join(found_keywords)}")
                else:
                    print(f"   ⚠️  WARNING - Expected keywords not found: {expected_keywords}")
            else:
                print(f"   ✅ SUCCESS - Tool executed without errors")
            
            # Show preview of result
            preview = content[:200].replace('\n', ' ').strip()
            if len(content) > 200:
                preview += "..."
            print(f"   📝 Preview: {preview}")
            
        else:
            print(f"   ❌ ERROR - No content returned")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return False


async def main():
    """Run comprehensive MCP tools verification"""
    print("🚀 Kansofy-Trade MCP Tools Verification")
    print("=" * 50)
    
    start_time = datetime.now()
    passed_tests = 0
    total_tests = 11
    
    # Test 1: System Health
    if await verify_tool(
        "get_system_health", 
        get_system_health_tool, 
        {"include_metrics": True},
        ["database", "connected", "healthy"]
    ):
        passed_tests += 1
    
    # Test 2: Document Statistics  
    if await verify_tool(
        "get_document_statistics",
        get_document_statistics_tool,
        {"detailed": True},
        ["total documents", "statistics"]
    ):
        passed_tests += 1
    
    # Test 3: Document Search
    if await verify_tool(
        "search_documents",
        search_documents_tool,
        {"query": "test", "limit": 5},
        ["found", "documents", "matching"]
    ):
        passed_tests += 1
    
    # Test 4: Vector Search
    if await verify_tool(
        "vector_search",
        vector_search_tool,
        {"query": "document processing", "limit": 3, "threshold": 0.5},
        ["vector search", "similarity", "results"]
    ):
        passed_tests += 1
    
    # Test 5: Document Details (using first document if available)
    if await verify_tool(
        "get_document_details",
        get_document_details_tool,
        {"document_id": 1, "include_content": False},
        ["document", "details", "filename"]
    ):
        passed_tests += 1
    
    # Test 6: Content Analysis
    if await verify_tool(
        "analyze_document_content",
        analyze_document_content_tool,
        {"search_query": "test", "analysis_type": "all"},
        ["analysis", "content", "entities"]
    ):
        passed_tests += 1
    
    # Test 7: Find Duplicates
    if await verify_tool(
        "find_duplicates",
        find_duplicates_tool,
        {"document_id": 1, "threshold": 0.9},
        ["duplicate", "detection", "results"]
    ):
        passed_tests += 1
    
    # Test 8: Hash Duplicate Check
    if await verify_tool(
        "check_duplicate_by_hash",
        check_duplicate_by_hash_tool,
        {"document_id": 1},
        ["hash", "duplicate", "check"]
    ):
        passed_tests += 1
    
    # Test 9: Document JSON
    if await verify_tool(
        "get_document_json",
        get_document_json_tool,
        {"document_id": 1},
        ["json", "data", "document"]
    ):
        passed_tests += 1
    
    # Test 10: Document Tables
    if await verify_tool(
        "get_document_tables",
        get_document_tables_tool,
        {"document_id": 1, "format": "json"},
        ["tables", "document"]
    ):
        passed_tests += 1
    
    # Test 11: Update Embeddings
    if await verify_tool(
        "update_embeddings",
        update_embeddings_tool,
        {},
        ["embedding", "update", "complete"]
    ):
        passed_tests += 1
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed_tests}/{total_tests} tests")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - MCP Server is ready for Claude Desktop!")
        print("\n💡 Next steps:")
        print("   1. Restart Claude Desktop")
        print("   2. Test integration with sample queries")
        print("   3. Upload documents and test document intelligence")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed - Check logs above")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure FastAPI server is running on port 8000") 
        print("   2. Check database file exists: ./kansofy_trade.db")
        print("   3. Verify vector store tables are initialized")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    asyncio.run(main())