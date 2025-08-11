#!/usr/bin/env python3
"""
Kansofy-Trade MCP Server

Model Context Protocol server providing Claude with document intelligence tools.
Enables semantic search, document analysis, and content extraction.
"""

import json
import logging
import asyncio
import aiosqlite
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, ImageContent, EmbeddedResource
)

# Import our application components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db_context, execute_raw_sql, search_documents_fts5
from app.core.config import get_settings
from app.models.document import DocumentStatus
from app.services.document_processor import DocumentProcessor
from app.core.vector_store import (
    init_vector_store, 
    search_similar_documents,
    find_duplicate_documents,
    update_all_embeddings
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kansofy-trade-mcp")

settings = get_settings()
document_processor = DocumentProcessor()
DATABASE_PATH = os.getenv("DATABASE_PATH", "./kansofy_trade.db")

# Initialize MCP Server
server = Server("kansofy-trade")

# MCP Tools Definition
TOOLS = [
    Tool(
        name="search_documents",
        description="Search documents using full-text search with FTS5. Supports phrase queries, boolean operators, and wildcard matching.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Supports: simple text, phrases in quotes, boolean operators (AND, OR), wildcards (*)",
                    "minLength": 1,
                    "maxLength": 500
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["query"]
        }
    ),
    
    Tool(
        name="get_document_details",
        description="Get detailed information about a specific document including content, metadata, and extracted entities.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "The ID of the document to retrieve"
                },
                "include_content": {
                    "type": "boolean",
                    "description": "Whether to include the full extracted text content",
                    "default": False
                }
            },
            "required": ["document_id"]
        }
    ),
    
    Tool(
        name="get_document_statistics",
        description="Get comprehensive statistics about the document collection including counts, types, processing status, and quality metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Return detailed breakdown by categories",
                    "default": True
                }
            }
        }
    ),
    
    Tool(
        name="analyze_document_content", 
        description="Analyze document content for patterns, entities, and insights. Can analyze a specific document or search results.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "ID of specific document to analyze"
                },
                "search_query": {
                    "type": "string",
                    "description": "Search query to find documents for analysis"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["entities", "summary", "patterns", "all"],
                    "description": "Type of analysis to perform",
                    "default": "all"
                }
            },
            "oneOf": [
                {"required": ["document_id"]},
                {"required": ["search_query"]}
            ]
        }
    ),
    
    Tool(
        name="get_system_health",
        description="Check system health including database connectivity, document processing status, and performance metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "include_metrics": {
                    "type": "boolean",
                    "description": "Include detailed performance metrics",
                    "default": False
                }
            }
        }
    ),
    
    Tool(
        name="vector_search",
        description="Search documents using semantic similarity with vector embeddings. Finds documents with similar meaning even if they don't share exact keywords.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query",
                    "minLength": 1,
                    "maxLength": 1000
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                },
                "threshold": {
                    "type": "number",
                    "description": "Minimum similarity score (0-1)",
                    "default": 0.5,
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["query"]
        }
    ),
    
    Tool(
        name="find_duplicates",
        description="Find potential duplicate documents based on content similarity using vector embeddings.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "ID of the document to check for duplicates"
                },
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold for duplicates (0-1)",
                    "default": 0.9,
                    "minimum": 0.7,
                    "maximum": 1.0
                }
            },
            "required": ["document_id"]
        }
    ),
    
    Tool(
        name="update_embeddings",
        description="Update vector embeddings for all documents that don't have them yet. Run this after uploading new documents to enable vector search.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    
    Tool(
        name="get_document_json",
        description="Get the full JSON representation of a document including all text, chunks, embeddings, and metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "ID of the document to retrieve JSON for"
                }
            },
            "required": ["document_id"]
        }
    ),
    
    Tool(
        name="check_duplicate_by_hash",
        description="Check if a document with the same content hash already exists in the database.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "ID of the document to check"
                }
            },
            "required": ["document_id"]
        }
    ),
    
    Tool(
        name="get_document_tables",
        description="Get extracted tables from a document. Tables are automatically extracted during document processing.",
        inputSchema={
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "ID of the document to get tables from"
                },
                "format": {
                    "type": "string",
                    "description": "Output format for tables",
                    "enum": ["json", "csv", "html", "text"],
                    "default": "json"
                }
            },
            "required": ["document_id"]
        }
    ),
    
    Tool(
        name="process_pending_documents",
        description="Process all documents that are uploaded but not yet processed (status: pending or uploaded)",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    
    Tool(
        name="upload_document",
        description="Upload a document for processing. Provide either file_path for local files or base64_content for direct upload.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to a local file to upload"
                },
                "filename": {
                    "type": "string",
                    "description": "Filename for the uploaded document (required if using base64_content)"
                },
                "base64_content": {
                    "type": "string",
                    "description": "Base64 encoded file content (alternative to file_path)"
                },
                "category": {
                    "type": "string",
                    "description": "Document category",
                    "enum": ["contract", "invoice", "report", "email", "presentation", "other"],
                    "default": "other"
                },
                "process_immediately": {
                    "type": "boolean",
                    "description": "Whether to process the document immediately",
                    "default": True
                }
            }
        }
    )
]


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool execution"""
    logger.info(f"🔧 Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "search_documents":
            return await search_documents_tool(arguments)
        elif name == "get_document_details":
            return await get_document_details_tool(arguments)
        elif name == "get_document_statistics":
            return await get_document_statistics_tool(arguments)
        elif name == "analyze_document_content":
            return await analyze_document_content_tool(arguments)
        elif name == "get_system_health":
            return await get_system_health_tool(arguments)
        elif name == "vector_search":
            return await vector_search_tool(arguments)
        elif name == "find_duplicates":
            return await find_duplicates_tool(arguments)
        elif name == "update_embeddings":
            return await update_embeddings_tool(arguments)
        elif name == "get_document_json":
            return await get_document_json_tool(arguments)
        elif name == "check_duplicate_by_hash":
            return await check_duplicate_by_hash_tool(arguments)
        elif name == "get_document_tables":
            return await get_document_tables_tool(arguments)
        elif name == "upload_document":
            return await upload_document_tool(arguments)
        elif name == "process_pending_documents":
            return await process_pending_documents_tool(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(
            type="text", 
            text=f"Tool execution failed: {str(e)}"
        )]


async def search_documents_tool(arguments: dict) -> list[TextContent]:
    """Search documents using FTS5 full-text search"""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 10)
    
    if not query.strip():
        return [TextContent(type="text", text="Search query cannot be empty")]
    
    try:
        # Execute FTS5 search
        results = await search_documents_fts5(query, limit)
        
        if not results:
            return [TextContent(
                type="text",
                text=f"No documents found matching query: '{query}'"
            )]
        
        # Format results
        response = f"📄 Found {len(results)} documents matching '{query}':\\n\\n"
        
        for i, doc in enumerate(results, 1):
            response += f"**{i}. {doc['filename']}**\\n"
            response += f"   ID: {doc['id']} | Size: {doc['file_size']:,} bytes\\n"
            response += f"   Uploaded: {doc['uploaded_at']}\\n"
            
            if doc.get('snippet'):
                # Clean up snippet
                snippet = doc['snippet'].replace('<mark>', '**').replace('</mark>', '**')
                response += f"   Preview: {snippet}\\n"
            
            response += f"   Relevance: {doc.get('relevance_score', 0.0):.3f}\\n\\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return [TextContent(type="text", text=f"Search operation failed: {str(e)}")]


async def get_document_details_tool(arguments: dict) -> list[TextContent]:
    """Get detailed document information"""
    document_id = arguments.get("document_id")
    include_content = arguments.get("include_content", False)
    
    if not document_id:
        return [TextContent(type="text", text="Document ID is required")]
    
    try:
        # Query document details
        query = """
            SELECT id, filename, original_filename, file_size, content_type, status,
                   content, doc_metadata, entities, summary, confidence_score,
                   uploaded_at, processed_at, updated_at
            FROM documents 
            WHERE id = ?
        """
        
        results = await execute_raw_sql(query, [document_id])
        
        if not results:
            return [TextContent(
                type="text", 
                text=f"Document with ID {document_id} not found"
            )]
        
        doc = results[0]
        
        # Format response
        response = f"📄 **Document Details**\\n\\n"
        response += f"**ID:** {doc['id']}\\n"
        response += f"**Filename:** {doc['filename']}\\n"
        response += f"**Original Name:** {doc['original_filename']}\\n"
        response += f"**Size:** {doc['file_size']:,} bytes\\n"
        response += f"**Type:** {doc['content_type'] or 'Unknown'}\\n"
        response += f"**Status:** {doc['status']}\\n"
        response += f"**Confidence:** {doc['confidence_score']:.3f}\\n"
        response += f"**Uploaded:** {doc['uploaded_at']}\\n"
        
        if doc['processed_at']:
            response += f"**Processed:** {doc['processed_at']}\\n"
        
        # Add entities if available
        if doc['entities']:
            try:
                entities = json.loads(doc['entities']) if isinstance(doc['entities'], str) else doc['entities']
                response += "\\n**📋 Extracted Entities:**\\n"
                
                for category, items in entities.items():
                    if items:
                        response += f"- **{category.title()}:** {', '.join(items)}\\n"
            except Exception as e:
                logger.warning(f"Failed to parse entities: {e}")
        
        # Add summary if available
        if doc['summary']:
            response += f"\\n**📝 Summary:**\\n{doc['summary']}\\n"
        
        # Add metadata if available
        if doc['doc_metadata']:
            try:
                metadata = json.loads(doc['doc_metadata']) if isinstance(doc['doc_metadata'], str) else doc['doc_metadata']
                response += f"\\n**🏷️ Metadata:**\\n{json.dumps(metadata, indent=2)}\\n"
            except Exception as e:
                logger.warning(f"Failed to parse metadata: {e}")
        
        # Add content if requested
        if include_content and doc['content']:
            content_preview = doc['content'][:1000]
            if len(doc['content']) > 1000:
                content_preview += "... (truncated)"
            response += f"\\n**📄 Content Preview:**\\n```\\n{content_preview}\\n```\\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to get document details: {e}")
        return [TextContent(type="text", text=f"Failed to retrieve document details: {str(e)}")]


async def get_document_statistics_tool(arguments: dict) -> list[TextContent]:
    """Get document collection statistics"""
    detailed = arguments.get("detailed", True)
    
    try:
        # Basic statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_documents,
                SUM(file_size) as total_size,
                AVG(confidence_score) as avg_confidence,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_docs,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_docs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_docs,
                COUNT(CASE WHEN uploaded_at >= datetime('now', '-1 day') THEN 1 END) as recent_uploads
            FROM documents
        """
        
        stats_results = await execute_raw_sql(stats_query)
        stats = stats_results[0] if stats_results else {}
        
        # Format response
        response = "📊 **Document Collection Statistics**\\n\\n"
        response += f"**Total Documents:** {stats.get('total_documents', 0):,}\\n"
        response += f"**Total Size:** {stats.get('total_size', 0) / 1024 / 1024:.1f} MB\\n"
        response += f"**Average Confidence:** {stats.get('avg_confidence', 0):.3f}\\n"
        response += f"**Recent Uploads (24h):** {stats.get('recent_uploads', 0)}\\n\\n"
        
        response += f"**📈 Processing Status:**\\n"
        response += f"- ✅ Completed: {stats.get('completed_docs', 0)}\\n"
        response += f"- 🔄 Processing: {stats.get('processing_docs', 0)}\\n"
        response += f"- ❌ Failed: {stats.get('failed_docs', 0)}\\n\\n"
        
        if detailed:
            # Content type breakdown
            content_type_query = """
                SELECT content_type, COUNT(*) as count, SUM(file_size) as total_size
                FROM documents 
                WHERE content_type IS NOT NULL
                GROUP BY content_type 
                ORDER BY count DESC
            """
            
            content_types = await execute_raw_sql(content_type_query)
            
            if content_types:
                response += "**📄 By Content Type:**\\n"
                for ct in content_types:
                    size_mb = ct['total_size'] / 1024 / 1024
                    response += f"- {ct['content_type']}: {ct['count']} files ({size_mb:.1f} MB)\\n"
                response += "\\n"
            
            # Recent activity
            recent_query = """
                SELECT DATE(uploaded_at) as upload_date, COUNT(*) as count
                FROM documents 
                WHERE uploaded_at >= datetime('now', '-7 days')
                GROUP BY DATE(uploaded_at)
                ORDER BY upload_date DESC
            """
            
            recent_activity = await execute_raw_sql(recent_query)
            
            if recent_activity:
                response += "**📅 Recent Activity (Last 7 Days):**\\n"
                for day in recent_activity:
                    response += f"- {day['upload_date']}: {day['count']} uploads\\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return [TextContent(type="text", text=f"Failed to retrieve statistics: {str(e)}")]


async def analyze_document_content_tool(arguments: dict) -> list[TextContent]:
    """Analyze document content for patterns and insights"""
    document_id = arguments.get("document_id")
    search_query = arguments.get("search_query")
    analysis_type = arguments.get("analysis_type", "all")
    
    if not document_id and not search_query:
        return [TextContent(type="text", text="Either document_id or search_query is required")]
    
    try:
        documents = []
        
        if document_id:
            # Analyze specific document
            doc_query = """
                SELECT id, filename, content, entities, summary, confidence_score
                FROM documents 
                WHERE id = ? AND status = 'completed'
            """
            doc_results = await execute_raw_sql(doc_query, [document_id])
            documents = doc_results
            
        elif search_query:
            # Find documents matching search query
            search_results = await search_documents_fts5(search_query, 5)
            doc_ids = [str(doc['id']) for doc in search_results]
            
            if doc_ids:
                placeholders = ','.join(['?' for _ in doc_ids])
                doc_query = f"""
                    SELECT id, filename, content, entities, summary, confidence_score
                    FROM documents 
                    WHERE id IN ({placeholders}) AND status = 'completed'
                """
                documents = await execute_raw_sql(doc_query, doc_ids)
        
        if not documents:
            return [TextContent(
                type="text",
                text="No completed documents found for analysis"
            )]
        
        # Perform analysis
        response = "🔍 **Document Content Analysis**\\n\\n"
        response += f"**Analyzed {len(documents)} document(s)**\\n\\n"
        
        # Aggregate analysis
        all_entities = {}
        total_content_length = 0
        avg_confidence = 0
        
        for doc in documents:
            total_content_length += len(doc['content']) if doc['content'] else 0
            avg_confidence += doc['confidence_score'] or 0
            
            # Parse entities
            if doc['entities']:
                try:
                    entities = json.loads(doc['entities']) if isinstance(doc['entities'], str) else doc['entities']
                    for category, items in entities.items():
                        if category not in all_entities:
                            all_entities[category] = []
                        all_entities[category].extend(items)
                except Exception as e:
                    logger.warning(f"Failed to parse entities for doc {doc['id']}: {e}")
        
        avg_confidence /= len(documents)
        
        # Format results based on analysis type
        if analysis_type in ["entities", "all"]:
            response += "**🏷️ Extracted Entities:**\\n"
            for category, items in all_entities.items():
                if items:
                    unique_items = list(set(items))[:10]  # Top 10 unique items
                    response += f"- **{category.title()}:** {', '.join(unique_items)}\\n"
            response += "\\n"
        
        if analysis_type in ["summary", "all"]:
            response += "**📝 Key Insights:**\\n"
            response += f"- Average processing confidence: {avg_confidence:.3f}\\n"
            response += f"- Total content analyzed: {total_content_length:,} characters\\n"
            response += f"- Average content per document: {total_content_length // len(documents):,} characters\\n"
            
            # Most common entities
            entity_counts = {}
            for category, items in all_entities.items():
                entity_counts[category] = len(set(items))
            
            if entity_counts:
                max_category = max(entity_counts.items(), key=lambda x: x[1])
                response += f"- Most diverse entity type: {max_category[0]} ({max_category[1]} unique items)\\n"
            
            response += "\\n"
        
        if analysis_type in ["patterns", "all"]:
            response += "**📊 Content Patterns:**\\n"
            
            # Analyze filenames for patterns
            extensions = {}
            for doc in documents:
                filename = doc['filename']
                if '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            if extensions:
                response += "- File types: "
                response += ", ".join([f"{ext} ({count})" for ext, count in extensions.items()])
                response += "\\n"
            
            # Content length distribution
            lengths = [len(doc['content']) if doc['content'] else 0 for doc in documents]
            if lengths:
                response += f"- Content length range: {min(lengths):,} - {max(lengths):,} characters\\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        return [TextContent(type="text", text=f"Content analysis failed: {str(e)}")]


async def get_system_health_tool(arguments: dict) -> list[TextContent]:
    """Check system health and performance"""
    include_metrics = arguments.get("include_metrics", False)
    
    try:
        response = "🏥 **System Health Check**\\n\\n"
        
        # Database connectivity
        try:
            db_test = await execute_raw_sql("SELECT 1 as test")
            db_healthy = len(db_test) > 0
        except Exception:
            db_healthy = False
        
        response += f"**Database:** {'✅ Connected' if db_healthy else '❌ Disconnected'}\\n"
        
        # FTS5 search capability
        try:
            fts_test = await execute_raw_sql("SELECT count(*) FROM document_search")
            fts_healthy = True
        except Exception:
            fts_healthy = False
        
        response += f"**Search Index:** {'✅ Available' if fts_healthy else '❌ Unavailable'}\\n"
        
        # Upload directory
        upload_dir_healthy = settings.upload_path.exists() and settings.upload_path.is_dir()
        response += f"**Upload Directory:** {'✅ Ready' if upload_dir_healthy else '❌ Not Ready'}\\n"
        
        # Processing status
        processing_query = """
            SELECT 
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_count,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
            FROM documents
        """
        
        processing_stats = await execute_raw_sql(processing_query)
        if processing_stats:
            stats = processing_stats[0]
            processing_count = stats.get('processing_count', 0)
            failed_count = stats.get('failed_count', 0)
            
            response += f"**Processing Queue:** {processing_count} active, {failed_count} failed\\n"
        
        # Overall health
        overall_healthy = all([db_healthy, fts_healthy, upload_dir_healthy])
        response += f"\\n**Overall Status:** {'✅ Healthy' if overall_healthy else '⚠️ Issues Detected'}\\n"
        
        if include_metrics:
            response += "\\n**📊 Performance Metrics:**\\n"
            
            # Database performance
            perf_start = datetime.now()
            await execute_raw_sql("SELECT COUNT(*) FROM documents")
            perf_time = (datetime.now() - perf_start).total_seconds()
            response += f"- Database query latency: {perf_time:.3f}s\\n"
            
            # Disk usage
            if settings.upload_path.exists():
                total_size = sum(f.stat().st_size for f in settings.upload_path.glob('**/*') if f.is_file())
                response += f"- Upload directory size: {total_size / 1024 / 1024:.1f} MB\\n"
            
            # Configuration
            response += f"- Max file size: {settings.max_file_size / 1024 / 1024:.1f} MB\\n"
            response += f"- Allowed extensions: {', '.join(settings.allowed_extensions)}\\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return [TextContent(type="text", text=f"Health check failed: {str(e)}")]


async def vector_search_tool(arguments: dict) -> list[TextContent]:
    """Search documents using vector similarity"""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 10)
    threshold = arguments.get("threshold", 0.5)
    
    if not query.strip():
        return [TextContent(type="text", text="Search query cannot be empty")]
    
    try:
        # Perform vector search
        results = await search_similar_documents(query, limit, threshold)
        
        if not results:
            return [TextContent(
                type="text",
                text=f"No documents found with similarity ≥ {threshold:.1%} for query: '{query}'"
            )]
        
        # Format results
        response = f"🔮 **Vector Search Results**\n"
        response += f"Query: '{query}'\n"
        response += f"Found {len(results)} similar document chunks:\n\n"
        
        # Group results by document
        docs_seen = set()
        for i, result in enumerate(results, 1):
            doc_id = result['document_id']
            
            # Show document header only once
            if doc_id not in docs_seen:
                response += f"**📄 {result['filename']}** (ID: {doc_id})\n"
                docs_seen.add(doc_id)
            
            # Show chunk details
            response += f"  • Chunk {result['chunk_index'] + 1}: "
            response += f"**{result['similarity_score']:.1%}** similarity\n"
            
            # Show preview of chunk text
            preview = result['chunk_text'][:200]
            if len(result['chunk_text']) > 200:
                preview += "..."
            response += f"    {preview}\n\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return [TextContent(type="text", text=f"Vector search failed: {str(e)}")]


async def find_duplicates_tool(arguments: dict) -> list[TextContent]:
    """Find duplicate documents based on content similarity"""
    document_id = arguments.get("document_id")
    threshold = arguments.get("threshold", 0.9)
    
    if not document_id:
        return [TextContent(type="text", text="Document ID is required")]
    
    try:
        # Find duplicates
        duplicates = await find_duplicate_documents(document_id, threshold)
        
        if not duplicates:
            return [TextContent(
                type="text",
                text=f"No duplicate documents found with similarity ≥ {threshold:.1%}"
            )]
        
        # Format results
        response = f"🔍 **Duplicate Detection Results**\n"
        response += f"Checking document ID: {document_id}\n"
        response += f"Similarity threshold: {threshold:.1%}\n\n"
        response += f"**Found {len(duplicates)} potential duplicate(s):**\n\n"
        
        for i, dup in enumerate(duplicates, 1):
            response += f"{i}. **{dup['filename']}** (ID: {dup['document_id']})\n"
            response += f"   • Max similarity: **{dup['max_similarity']:.1%}**\n"
            response += f"   • Matching chunks: {dup['matching_chunks']}\n\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        return [TextContent(type="text", text=f"Duplicate detection failed: {str(e)}")]


async def update_embeddings_tool(arguments: dict) -> list[TextContent]:
    """Update embeddings for all documents"""
    try:
        logger.info("Starting embedding update for all documents...")
        
        # Update embeddings
        total_count = await update_all_embeddings()
        
        response = "✨ **Embedding Update Complete**\n\n"
        
        if total_count == 0:
            response += "All documents already have embeddings. No updates needed."
        else:
            response += f"Successfully generated **{total_count}** embeddings.\n"
            response += "Vector search is now available for all processed documents."
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Embedding update failed: {e}")
        return [TextContent(type="text", text=f"Embedding update failed: {str(e)}")]


async def get_document_json_tool(arguments: dict) -> list[TextContent]:
    """Get the full JSON representation of a document"""
    document_id = arguments.get("document_id")
    
    if not document_id:
        return [TextContent(type="text", text="Document ID is required")]
    
    try:
        # Query for full JSON data
        query = """
        SELECT id, filename, file_hash, full_text_json, content, uploaded_at
        FROM documents
        WHERE id = ?
        """
        
        results = await execute_raw_sql(query, [document_id])
        
        if not results:
            return [TextContent(
                type="text",
                text=f"Document with ID {document_id} not found"
            )]
        
        doc = results[0]
        
        # Format response
        response = f"📋 **Document JSON Data**\n\n"
        response += f"**ID:** {doc['id']}\n"
        response += f"**Filename:** {doc['filename']}\n"
        response += f"**File Hash:** {doc['file_hash'] or 'Not generated'}\n"
        response += f"**Uploaded:** {doc['uploaded_at']}\n\n"
        
        if doc['full_text_json']:
            try:
                full_json = json.loads(doc['full_text_json']) if isinstance(doc['full_text_json'], str) else doc['full_text_json']
                
                # Show summary statistics
                response += "**📊 JSON Statistics:**\n"
                response += f"- Document Hash: {full_json.get('document_hash', 'N/A')[:16]}...\n"
                response += f"- Content Length: {full_json.get('content_length', 0):,} characters\n"
                response += f"- Chunks Count: {full_json.get('chunks_count', 0)}\n"
                response += f"- Embedding Model: {full_json.get('embedding_model', 'N/A')}\n"
                response += f"- Embedding Dimensions: {full_json.get('embedding_dimensions', 0)}\n\n"
                
                # Show metadata
                if full_json.get('metadata'):
                    response += "**🏷️ Metadata:**\n```json\n"
                    response += json.dumps(full_json['metadata'], indent=2)[:500]
                    response += "\n```\n\n"
                
                # Show first chunk as sample
                if full_json.get('chunks') and len(full_json['chunks']) > 0:
                    first_chunk = full_json['chunks'][0]
                    response += "**📄 First Chunk Sample:**\n"
                    response += f"- Index: {first_chunk.get('index', 0)}\n"
                    response += f"- Hash: {first_chunk.get('hash', 'N/A')[:16]}...\n"
                    response += f"- Length: {first_chunk.get('length', 0)} characters\n"
                    response += f"- Text Preview: {first_chunk.get('text', '')[:100]}...\n"
                    response += f"- Embedding: [{first_chunk.get('embedding', [])[0]:.4f}, ...] (dim: {len(first_chunk.get('embedding', []))})\n"
                
            except Exception as e:
                logger.warning(f"Failed to parse full_text_json: {e}")
                response += f"**Error parsing JSON:** {str(e)}\n"
        else:
            response += "**No JSON data available** - Document may not have been fully processed yet.\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to get document JSON: {e}")
        return [TextContent(type="text", text=f"Failed to retrieve document JSON: {str(e)}")]


async def check_duplicate_by_hash_tool(arguments: dict) -> list[TextContent]:
    """Check for duplicate documents by hash"""
    document_id = arguments.get("document_id")
    
    if not document_id:
        return [TextContent(type="text", text="Document ID is required")]
    
    try:
        # Get the hash of the specified document
        query = """
        SELECT id, filename, file_hash, uploaded_at
        FROM documents
        WHERE id = ?
        """
        
        results = await execute_raw_sql(query, [document_id])
        
        if not results:
            return [TextContent(
                type="text",
                text=f"Document with ID {document_id} not found"
            )]
        
        doc = results[0]
        file_hash = doc['file_hash']
        
        if not file_hash:
            return [TextContent(
                type="text",
                text=f"Document {document_id} does not have a hash generated yet"
            )]
        
        # Find all documents with the same hash
        duplicate_query = """
        SELECT id, filename, uploaded_at, file_size, status
        FROM documents
        WHERE file_hash = ? AND id != ?
        ORDER BY uploaded_at DESC
        """
        
        duplicates = await execute_raw_sql(duplicate_query, [file_hash, document_id])
        
        # Format response
        response = f"🔍 **Hash-Based Duplicate Check**\n\n"
        response += f"**Document:** {doc['filename']} (ID: {document_id})\n"
        response += f"**File Hash:** {file_hash[:16]}...\n\n"
        
        if duplicates:
            response += f"⚠️ **Found {len(duplicates)} exact duplicate(s):**\n\n"
            
            for i, dup in enumerate(duplicates, 1):
                response += f"{i}. **{dup['filename']}** (ID: {dup['id']})\n"
                response += f"   • Uploaded: {dup['uploaded_at']}\n"
                response += f"   • Size: {dup['file_size']:,} bytes\n"
                response += f"   • Status: {dup['status']}\n\n"
            
            response += "💡 **Note:** These documents have identical content (same SHA-256 hash).\n"
        else:
            response += "✅ **No exact duplicates found.**\n"
            response += "This document appears to be unique in the database.\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        return [TextContent(type="text", text=f"Duplicate check failed: {str(e)}")]


async def process_pending_documents_tool(arguments: dict) -> list[TextContent]:
    """Process all pending documents"""
    
    try:
        # Find pending documents
        query = """
            SELECT id, filename, file_size 
            FROM documents 
            WHERE status IN ('pending', 'uploaded')
            ORDER BY uploaded_at ASC
        """
        
        pending_docs = await execute_raw_sql(query)
        
        if not pending_docs:
            return [TextContent(
                type="text",
                text="✅ No pending documents to process. All documents are up to date."
            )]
        
        response = f"📋 **Processing {len(pending_docs)} Pending Document(s)**\n\n"
        
        from app.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        success_count = 0
        fail_count = 0
        
        for doc in pending_docs:
            doc_id = doc['id']
            filename = doc['filename']
            file_size = doc['file_size']
            
            response += f"**Document {doc_id}:** {filename} ({file_size / 1024:.1f} KB)\n"
            
            try:
                # Process the document
                result = await processor.process_document_async(doc_id)
                
                if result:
                    response += f"  ✅ Processed successfully\n"
                    success_count += 1
                else:
                    response += f"  ❌ Processing failed\n"
                    fail_count += 1
                    
            except Exception as e:
                response += f"  ❌ Error: {str(e)}\n"
                fail_count += 1
                logger.error(f"Failed to process document {doc_id}: {e}")
        
        response += f"\n**Summary:**\n"
        response += f"- ✅ Successfully processed: {success_count}\n"
        response += f"- ❌ Failed: {fail_count}\n"
        response += f"- 📊 Total: {len(pending_docs)}\n"
        
        if success_count > 0:
            response += f"\n💡 Processed documents are now searchable and ready for analysis."
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Batch processing failed: {str(e)}"
        )]


async def upload_document_tool(arguments: dict) -> list[TextContent]:
    """Upload a document for processing"""
    import base64
    import hashlib
    import uuid
    from pathlib import Path
    from datetime import datetime
    
    file_path = arguments.get("file_path")
    base64_content = arguments.get("base64_content")
    filename = arguments.get("filename")
    category = arguments.get("category", "other")
    process_immediately = arguments.get("process_immediately", True)
    
    # Validate input
    if not file_path and not base64_content:
        return [TextContent(
            type="text",
            text="❌ Error: Please provide either file_path or base64_content"
        )]
    
    if base64_content and not filename:
        return [TextContent(
            type="text",
            text="❌ Error: filename is required when using base64_content"
        )]
    
    try:
        # Prepare file content
        if file_path:
            # Read from local file
            path = Path(file_path)
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"❌ Error: File not found: {file_path}"
                )]
            
            filename = path.name
            file_content = path.read_bytes()
            file_size = len(file_content)
        else:
            # Decode base64 content
            try:
                file_content = base64.b64decode(base64_content)
                file_size = len(file_content)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error decoding base64 content: {e}"
                )]
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            return [TextContent(
                type="text",
                text=f"❌ Error: File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 50MB"
            )]
        
        # Check file extension
        file_ext = Path(filename).suffix.lower().strip('.')
        allowed_extensions = ["pdf", "docx", "txt", "xlsx", "csv"]
        if file_ext not in allowed_extensions:
            return [TextContent(
                type="text",
                text=f"❌ Error: Unsupported file type '.{file_ext}'. Allowed types: {', '.join(allowed_extensions)}"
            )]
        
        # Generate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicates
        duplicate_query = """
            SELECT id, filename, uploaded_at 
            FROM documents 
            WHERE file_hash = ?
            LIMIT 1
        """
        duplicates = await execute_raw_sql(duplicate_query, (file_hash,))
        
        if duplicates:
            dup = duplicates[0]
            return [TextContent(
                type="text",
                text=f"⚠️ **Duplicate Document Detected**\n\n"
                     f"This file already exists in the system:\n"
                     f"- **ID:** {dup['id']}\n"
                     f"- **Filename:** {dup['filename']}\n"
                     f"- **Uploaded:** {dup['uploaded_at']}\n\n"
                     f"File hash: {file_hash[:16]}..."
            )]
        
        # Save file to upload directory
        upload_dir = Path(os.getenv("UPLOAD_PATH", "./uploads"))
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        safe_filename = f"{unique_id}_{filename}"
        file_path_full = upload_dir / safe_filename
        
        # Write file
        file_path_full.write_bytes(file_content)
        
        # Determine content type
        content_type_map = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv"
        }
        content_type = content_type_map.get(file_ext, "application/octet-stream")
        
        # Insert into database
        insert_query = """
            INSERT INTO documents (
                uuid, filename, original_filename, file_path, file_size,
                content_type, file_hash, category, status, uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(insert_query, (
                unique_id,
                safe_filename,
                filename,
                str(file_path_full),
                file_size,
                content_type,
                file_hash,
                category,
                "pending" if process_immediately else "uploaded",
                datetime.now().isoformat()
            ))
            await db.commit()
            document_id = cursor.lastrowid
        
        # Process document if requested
        if process_immediately:
            # Import document processor
            from app.services.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            
            try:
                # Process the document using the async wrapper
                await processor.process_document_async(document_id)
                
                # Get updated status
                status_query = "SELECT status FROM documents WHERE id = ?"
                result = await execute_raw_sql(status_query, (document_id,))
                status = result[0]['status'] if result else "unknown"
                
                response = f"✅ **Document Uploaded and Processed Successfully**\n\n"
                response += f"- **Document ID:** {document_id}\n"
                response += f"- **Filename:** {filename}\n"
                response += f"- **Size:** {file_size / 1024:.1f} KB\n"
                response += f"- **Type:** {file_ext.upper()}\n"
                response += f"- **Category:** {category}\n"
                response += f"- **Status:** {status}\n"
                response += f"- **Hash:** {file_hash[:16]}...\n\n"
                response += f"📝 Document has been processed and is ready for search and analysis."
                
            except Exception as e:
                logger.error(f"Processing failed: {e}")
                response = f"✅ **Document Uploaded Successfully**\n\n"
                response += f"- **Document ID:** {document_id}\n"
                response += f"- **Filename:** {filename}\n"
                response += f"- **Size:** {file_size / 1024:.1f} KB\n\n"
                response += f"⚠️ Processing failed: {str(e)}\n"
                response += f"The document is uploaded but needs manual processing."
        else:
            response = f"✅ **Document Uploaded Successfully**\n\n"
            response += f"- **Document ID:** {document_id}\n"
            response += f"- **Filename:** {filename}\n"
            response += f"- **Size:** {file_size / 1024:.1f} KB\n"
            response += f"- **Type:** {file_ext.upper()}\n"
            response += f"- **Category:** {category}\n"
            response += f"- **Status:** uploaded (not processed)\n"
            response += f"- **Hash:** {file_hash[:16]}...\n\n"
            response += f"💡 Use `update_embeddings` to process this document later."
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return [TextContent(
            type="text",
            text=f"❌ Upload failed: {str(e)}"
        )]


async def get_document_tables_tool(arguments: dict) -> list[TextContent]:
    """Get extracted tables from a document"""
    document_id = arguments.get("document_id")
    format_type = arguments.get("format", "json")
    
    if not document_id:
        return [TextContent(type="text", text="Document ID is required")]
    
    try:
        # Query for document tables
        query = """
        SELECT id, filename, tables, status, uploaded_at
        FROM documents
        WHERE id = ?
        """
        
        results = await execute_raw_sql(query, [document_id])
        
        if not results:
            return [TextContent(
                type="text",
                text=f"Document with ID {document_id} not found"
            )]
        
        doc = results[0]
        
        # Check if document has been processed
        if doc['status'] != 'completed':
            return [TextContent(
                type="text",
                text=f"Document {document_id} has not been fully processed yet (status: {doc['status']})"
            )]
        
        # Format response
        response = f"📊 **Document Tables**\n\n"
        response += f"**Document:** {doc['filename']} (ID: {document_id})\n"
        response += f"**Uploaded:** {doc['uploaded_at']}\n\n"
        
        if not doc['tables']:
            response += "📭 **No tables found in this document.**\n"
            response += "Tables are automatically extracted from PDFs, Word docs, and other structured documents during processing.\n"
            return [TextContent(type="text", text=response)]
        
        try:
            # Parse tables JSON
            tables = json.loads(doc['tables']) if isinstance(doc['tables'], str) else doc['tables']
            
            if not tables or (isinstance(tables, list) and len(tables) == 0):
                response += "📭 **No tables found in this document.**\n"
                return [TextContent(type="text", text=response)]
            
            response += f"**Found {len(tables)} table(s):**\n\n"
            
            # Format tables based on requested format
            for idx, table in enumerate(tables):
                response += f"### 📋 Table {idx + 1}\n"
                
                # Add caption if available
                if table.get('caption'):
                    response += f"**Caption:** {table['caption']}\n"
                
                if format_type == "json":
                    # JSON format - show structure
                    response += "```json\n"
                    # Show a condensed version of the table
                    table_summary = {
                        "index": table.get('index', idx),
                        "rows_count": len(table.get('rows', [])),
                        "has_headers": bool(table.get('headers')),
                        "type": table.get('type', 'extracted_table')
                    }
                    if table.get('headers'):
                        table_summary['headers'] = table['headers']
                    if table.get('rows') and len(table['rows']) > 0:
                        # Show first 3 rows as sample
                        table_summary['sample_rows'] = table['rows'][:3]
                    
                    response += json.dumps(table_summary, indent=2)
                    response += "\n```\n"
                    
                elif format_type == "csv":
                    # CSV format
                    if table.get('csv'):
                        response += "```csv\n"
                        response += table['csv'][:1000]  # Limit to first 1000 chars
                        if len(table.get('csv', '')) > 1000:
                            response += "\n... (truncated)"
                        response += "\n```\n"
                    elif table.get('rows'):
                        # Convert rows to CSV format
                        response += "```csv\n"
                        if table.get('headers'):
                            response += ",".join(str(h) for h in table['headers']) + "\n"
                        for row in table.get('rows', [])[:5]:  # Show first 5 rows
                            if isinstance(row, list):
                                response += ",".join(str(cell) for cell in row) + "\n"
                            elif isinstance(row, dict):
                                response += ",".join(str(v) for v in row.values()) + "\n"
                        if len(table.get('rows', [])) > 5:
                            response += "... (showing first 5 rows)\n"
                        response += "```\n"
                    
                elif format_type == "html":
                    # HTML format
                    if table.get('html'):
                        response += "```html\n"
                        response += table['html'][:1000]  # Limit to first 1000 chars
                        if len(table.get('html', '')) > 1000:
                            response += "\n... (truncated)"
                        response += "\n```\n"
                    else:
                        response += "HTML format not available for this table.\n"
                
                else:  # text format
                    # Simple text representation
                    if table.get('content'):
                        response += table['content'][:500]
                        if len(table.get('content', '')) > 500:
                            response += "... (truncated)"
                        response += "\n"
                    elif table.get('rows'):
                        # Show rows as text
                        for i, row in enumerate(table.get('rows', [])[:5]):
                            response += f"Row {i+1}: {row}\n"
                        if len(table.get('rows', [])) > 5:
                            response += f"... and {len(table['rows']) - 5} more rows\n"
                
                response += "\n"
            
            # Add extraction tips
            response += "\n💡 **Tips:**\n"
            response += "- Tables are automatically extracted from PDFs, Word docs, and Excel files\n"
            response += "- Use format='csv' to get comma-separated values\n"
            response += "- Use format='json' to get structured data\n"
            response += "- Complex tables with merged cells may need manual review\n"
            
        except Exception as e:
            logger.warning(f"Failed to parse tables JSON: {e}")
            response += f"⚠️ **Error parsing table data:** {str(e)}\n"
            response += "The tables data may be corrupted or in an unexpected format.\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to get document tables: {e}")
        return [TextContent(type="text", text=f"Failed to retrieve document tables: {str(e)}")]


async def main():
    """Main entry point for MCP server"""
    logger.info("🚀 Starting Kansofy-Trade MCP Server")
    logger.info(f"📊 Database: {settings.database_path}")
    logger.info(f"📁 Upload directory: {settings.upload_path}")
    logger.info(f"🔧 Available tools: {len(TOOLS)}")
    
    # Initialize database
    from app.core.database import init_database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Initialize vector store
    await init_vector_store()
    logger.info("✅ Vector store initialized")
    
    # Start MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())