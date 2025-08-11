# Engine Capabilities Reference 🛠️

**14 deterministic operations that power your document workflows. No AI required.**

This engine provides the infrastructure for document operations - the actual intelligence comes from your AI assistant (Claude, Copilot, or any MCP client).

## Table of Contents
- [Quick Reference](#quick-reference)
- [Workflow Operations](#workflow-operations)
  - [upload_document](#1-upload_document)
  - [get_document_details](#2-get_document_details)
  - [get_document_tables](#3-get_document_tables)
  - [get_document_json](#4-get_document_json)
- [Discovery Operations](#discovery-operations)
  - [search_documents](#5-search_documents)
  - [vector_search](#6-vector_search)
  - [find_duplicates](#7-find_duplicates)
  - [check_duplicate_by_hash](#8-check_duplicate_by_hash)
- [Intelligence Operations](#intelligence-operations)
  - [analyze_document_content](#9-analyze_document_content)
  - [get_document_statistics](#10-get_document_statistics)
- [Engine Management](#engine-management)
  - [process_pending_documents](#11-process_pending_documents)
  - [update_embeddings](#12-update_embeddings)
  - [get_system_health](#13-get_system_health)
- [Advanced Usage](#advanced-usage)
- [Operation Workflows](#operation-workflows)
- [Error Handling](#error-handling)

## Quick Reference

**What This Enables**: Process 60-129 documents per shipment in minutes, not hours.

| Operation | Engine Capability | What This Enables |
|------|---------|------------------|
| `upload_document` | Docling extraction (no AI) | Process PDFs, extract tables deterministically |
| `search_documents` | SQLite FTS5 search (no AI) | Find documents instantly with SQL |
| `vector_search` | Pre-computed embeddings (no AI) | Discover similar documents without inference |
| `get_document_details` | Structured data retrieval | Access extracted information |
| `analyze_document_content` | Pattern detection (rule-based) | Identify entities and patterns |
| `get_document_statistics` | SQL aggregation | Track processing metrics |
| `find_duplicates` | Hash comparison | Detect duplicates deterministically |
| `update_embeddings` | Batch vector computation | Pre-compute for fast search |
| `get_document_tables` | Table extraction (Docling) | Extract tables without OCR/AI |
| `process_pending_documents` | Queue processing | Handle batch operations |
| `get_system_health` | Engine diagnostics | Monitor performance |
| `get_document_json` | Data export | Export structured data |
| `check_duplicate_by_hash` | SHA-256 verification | Exact duplicate detection |

---

## Workflow Operations

**Engine Infrastructure** (No AI Required) → **Your AI Adds Intelligence**

### 1. upload_document

**Engine Operation**: Deterministic document extraction using Docling (IBM Research).
**No AI Required**: Same document always produces same output.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `file_path` | string | No* | Path to local file | - |
| `base64_content` | string | No* | Base64 encoded content | - |
| `filename` | string | Yes** | Document filename | - |
| `category` | string | No | contract, invoice, report, email, presentation, other | "other" |
| `process_immediately` | boolean | No | Process document right away | true |

*One of `file_path` or `base64_content` required
**Required if using `base64_content`

**Example Usage:**

```python
# Upload local PDF file
result = upload_document(
    file_path="/Users/john/Documents/invoice_2024.pdf",
    category="invoice",
    process_immediately=True
)

# Response:
{
    "status": "success",
    "document_id": 42,
    "filename": "invoice_2024.pdf",
    "processing_status": "completed",
    "extracted_text_length": 2847,
    "tables_found": 3,
    "entities_extracted": 15,
    "processing_time": 2.3
}
```

**Real-World Example:**
```
User: "Upload and analyze this purchase order"
Claude: I'll upload and process that purchase order for you.

[Calls upload_document with file_path="PO_2024_0892.pdf", category="other"]

✅ Document uploaded successfully:
- Document ID: 89
- Extracted: 1,245 characters of text
- Found: 2 tables with line items
- Identified: vendor, dates, amounts, item codes
- Processing time: 1.8 seconds
```

---

### 2. get_document_details

Retrieve comprehensive information about a specific document.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `document_id` | integer | Yes | Document ID to retrieve | - |
| `include_content` | boolean | No | Include full text content | false |

**Example Usage:**

```python
# Get document metadata only
details = get_document_details(
    document_id=42,
    include_content=False
)

# Get document with full content
full_details = get_document_details(
    document_id=42,
    include_content=True
)

# Response:
{
    "id": 42,
    "filename": "Contract_CU_2024.pdf",
    "category": "contract",
    "file_size": 248539,
    "status": "completed",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "processed_at": "2024-01-15T10:30:02Z",
    "confidence_score": 0.95,
    "entities": {
        "parties": ["ACME Corp", "Global Supplies Ltd"],
        "dates": ["2024-01-15", "2024-12-31"],
        "amounts": ["$1,250,000", "10,000 MT"],
        "locations": ["Singapore", "Rotterdam"]
    },
    "summary": "Purchase agreement for copper cathodes...",
    "content": "Full extracted text..." // if include_content=True
}
```

---

### 3. get_document_tables

Extract structured tables from documents.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `document_id` | integer | Yes | Document ID | - |
| `format` | string | No | json, csv, html, text | "json" |

**Example Usage:**

```python
# Get tables as JSON
tables = get_document_tables(
    document_id=42,
    format="json"
)

# Response:
{
    "document_id": 42,
    "tables_count": 2,
    "tables": [
        {
            "table_index": 0,
            "title": "Price Schedule",
            "headers": ["Item", "Quantity", "Unit Price", "Total"],
            "rows": [
                ["Copper Cathode Grade A", "5,000 MT", "$9,450/MT", "$47,250,000"],
                ["Copper Cathode Grade B", "5,000 MT", "$9,200/MT", "$46,000,000"]
            ]
        }
    ]
}

# Get as CSV for spreadsheet import
csv_tables = get_document_tables(
    document_id=42,
    format="csv"
)
```

---

### 4. get_document_json

Export complete document data including embeddings.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | integer | Yes | Document ID |

**Example Usage:**

```python
# Export full document JSON
json_data = get_document_json(document_id=42)

# Response: Complete document structure
{
    "id": 42,
    "uuid": "6ac70e4d-76dc-4604-8072-22b1b5e69919",
    "filename": "contract.pdf",
    "metadata": {...},
    "content": "Full text...",
    "chunks": [
        {
            "text": "Chunk 1 text...",
            "embedding": [0.023, -0.127, ...],  # 384-dimensional vector
            "position": 0
        }
    ],
    "entities": {...},
    "tables": [...],
    "processing_log": [...]
}
```

---

## Discovery Operations

**Pure Database Operations** - No AI inference needed for search.

### 5. search_documents

**Engine Operation**: SQLite FTS5 full-text search.
**Deterministic**: Database queries, not AI predictions.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `query` | string | Yes | Search query (max 500 chars) | - |
| `limit` | integer | No | Maximum results (1-100) | 10 |

**Query Syntax:**
- Simple text: `copper shipment`
- Exact phrase: `"payment terms"`
- Boolean AND: `copper AND Chile`
- Boolean OR: `invoice OR receipt`
- Wildcard: `ship*` (matches shipping, shipment, etc.)
- Field search: `filename:invoice`

**Example Usage:**

```python
# Simple search
results = search_documents(
    query="copper cathode",
    limit=5
)

# Advanced search with operators
results = search_documents(
    query='"payment terms" AND (NET30 OR NET60)',
    limit=10
)

# Response:
{
    "query": "copper cathode",
    "results_count": 5,
    "documents": [
        {
            "id": 42,
            "filename": "Contract_CU_2024.pdf",
            "relevance_score": 0.98,
            "snippet": "...supply of **copper cathode** Grade A with 99.99% purity..."
        }
    ]
}
```

**Real-World Examples:**

```python
# Find invoices with specific payment terms
search_documents("invoice AND \"NET 30\"")

# Find all shipping documents from January
search_documents("shipping AND 2024-01-*")

# Find contracts mentioning both parties
search_documents("\"ACME Corp\" AND \"Global Supplies\"")

# Find documents with tables containing prices
search_documents("price OR pricing OR \"unit cost\"")
```

---

### 6. vector_search

**Engine Operation**: Pre-computed vector similarity (cosine distance).
**No AI Inference**: Embeddings are pre-calculated, search is pure math.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `query` | string | Yes | Natural language query (max 1000) | - |
| `limit` | integer | No | Maximum results (1-50) | 10 |
| `threshold` | float | No | Similarity threshold (0-1) | 0.5 |

**Example Usage:**

```python
# Find semantically similar documents
results = vector_search(
    query="legal agreements for metal commodities trading",
    limit=5,
    threshold=0.7
)

# Response:
{
    "query": "legal agreements for metal commodities trading",
    "results": [
        {
            "id": 42,
            "filename": "Copper_Purchase_Agreement.pdf",
            "similarity_score": 0.92,
            "preview": "Master purchase agreement for copper cathodes..."
        },
        {
            "id": 78,
            "filename": "Aluminum_Contract_2024.pdf",
            "similarity_score": 0.87,
            "preview": "Supply contract for aluminum ingots..."
        }
    ]
}
```

**Use Cases:**
- Find similar contracts without exact keywords
- Discover related documents across different categories
- Identify documents with similar concepts or topics
- Find precedents or templates

---

### 7. find_duplicates

Find potential duplicate documents based on content similarity.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `document_id` | integer | Yes | Document to check | - |
| `threshold` | float | No | Similarity threshold (0.7-1.0) | 0.9 |

**Example Usage:**

```python
# Check for near-duplicates
duplicates = find_duplicates(
    document_id=42,
    threshold=0.95
)

# Response:
{
    "source_document": {
        "id": 42,
        "filename": "Invoice_ABC123.pdf"
    },
    "potential_duplicates": [
        {
            "id": 89,
            "filename": "Invoice_ABC123_copy.pdf",
            "similarity": 0.98,
            "status": "likely_duplicate"
        },
        {
            "id": 156,
            "filename": "Invoice_ABC123_revised.pdf",
            "similarity": 0.91,
            "status": "possible_duplicate"
        }
    ]
}
```

---

### 8. check_duplicate_by_hash

Check for exact duplicates using content hash.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | integer | Yes | Document to check |

**Example Usage:**

```python
# Check for exact duplicates
result = check_duplicate_by_hash(document_id=42)

# Response:
{
    "document_id": 42,
    "content_hash": "a3f5e8b2c9d4...",
    "has_duplicate": true,
    "duplicate_documents": [
        {
            "id": 89,
            "filename": "Invoice_copy.pdf",
            "uploaded_at": "2024-01-10T08:15:00Z"
        }
    ]
}
```

---

## Intelligence Operations

**Pattern Recognition** - Rule-based extraction, not AI inference.

### 9. analyze_document_content

**Engine Operation**: Rule-based pattern matching and entity extraction.
**Deterministic**: Regular expressions and pattern rules, not AI.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `document_id` | integer | No* | Specific document ID | - |
| `search_query` | string | No* | Search for documents to analyze | - |
| `analysis_type` | string | No | entities, summary, patterns, all | "all" |

*One of `document_id` or `search_query` required

**Example Usage:**

```python
# Analyze specific document
analysis = analyze_document_content(
    document_id=42,
    analysis_type="all"
)

# Analyze search results
analysis = analyze_document_content(
    search_query="shipping documents 2024",
    analysis_type="patterns"
)

# Response:
{
    "analysis_type": "all",
    "documents_analyzed": 1,
    "entities": {
        "organizations": ["ACME Corp", "Global Shipping Ltd"],
        "dates": ["2024-01-15", "2024-02-28"],
        "monetary_amounts": ["$125,000", "€95,000"],
        "locations": ["Port of Singapore", "Rotterdam"],
        "products": ["Copper Cathode", "Grade A 99.99%"]
    },
    "patterns": {
        "payment_terms": ["NET 30", "2/10 NET 30"],
        "incoterms": ["FOB", "CIF"],
        "common_clauses": ["force majeure", "arbitration"]
    },
    "summary": "Purchase agreement for 10,000 MT of copper cathodes..."
}
```

---

### 10. get_document_statistics

Get comprehensive statistics about your document collection.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `detailed` | boolean | No | Include category breakdown | true |

**Example Usage:**

```python
# Get detailed statistics
stats = get_document_statistics(detailed=True)

# Response:
{
    "total_documents": 342,
    "total_size_bytes": 125789456,
    "total_size_readable": "120.0 MB",
    "status_breakdown": {
        "completed": 330,
        "processing": 5,
        "uploaded": 7,
        "failed": 0
    },
    "category_breakdown": {
        "invoice": 145,
        "contract": 89,
        "report": 67,
        "shipping": 34,
        "other": 7
    },
    "processing_stats": {
        "average_processing_time": 2.3,
        "success_rate": 0.98,
        "documents_with_tables": 234,
        "documents_with_embeddings": 330
    },
    "recent_uploads": [
        {
            "id": 342,
            "filename": "Invoice_2024_latest.pdf",
            "uploaded_at": "2024-01-20T14:30:00Z"
        }
    ]
}
```

---

## Engine Management

**Infrastructure Operations** - Maintain and monitor the engine.

### 11. process_pending_documents

Process all documents waiting in the queue.

**Parameters:**
None

**Example Usage:**

```python
# Process all pending documents
result = process_pending_documents()

# Response:
{
    "status": "success",
    "documents_processed": 7,
    "processing_time": 15.4,
    "results": [
        {
            "id": 340,
            "filename": "contract_1.pdf",
            "status": "completed",
            "processing_time": 2.1
        },
        {
            "id": 341,
            "filename": "invoice_2.pdf",
            "status": "completed",
            "processing_time": 1.8
        }
    ],
    "failed": []
}
```

---

### 12. update_embeddings

Update vector embeddings for documents without them.

**Parameters:**
None

**Example Usage:**

```python
# Update all missing embeddings
result = update_embeddings()

# Response:
{
    "status": "success",
    "documents_updated": 12,
    "processing_time": 8.7,
    "details": {
        "total_documents": 342,
        "already_had_embeddings": 330,
        "newly_embedded": 12,
        "failed": 0
    }
}
```

**When to Use:**
- After uploading documents with `process_immediately=False`
- After system updates that clear embeddings
- To enable vector search on older documents

---

### 13. get_system_health

Check system health and performance metrics.

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `include_metrics` | boolean | No | Include performance metrics | false |

**Example Usage:**

```python
# Basic health check
health = get_system_health(include_metrics=False)

# Detailed health with metrics
detailed_health = get_system_health(include_metrics=True)

# Response:
{
    "status": "healthy",
    "database": {
        "connected": true,
        "size_mb": 45.2,
        "document_count": 342
    },
    "services": {
        "document_processor": "operational",
        "vector_store": "operational",
        "search_index": "operational"
    },
    "metrics": {  // if include_metrics=True
        "avg_processing_time": 2.3,
        "search_avg_response_time": 0.045,
        "vector_search_avg_time": 0.089,
        "memory_usage_mb": 256,
        "cpu_usage_percent": 12.5,
        "uptime_hours": 168.5
    },
    "recent_errors": []
}
```

---

## Advanced Usage

### Operation Workflows

**Document Processing Pipeline (100% Deterministic):**
```python
# 1. Upload document
doc = upload_document(file_path="contract.pdf", category="contract")

# 2. Wait for processing
if doc["processing_status"] == "processing":
    time.sleep(3)

# 3. Analyze content
analysis = analyze_document_content(
    document_id=doc["document_id"],
    analysis_type="all"
)

# 4. Check for duplicates
duplicates = find_duplicates(
    document_id=doc["document_id"],
    threshold=0.9
)

# 5. Extract tables if present
if analysis["tables_found"] > 0:
    tables = get_document_tables(
        document_id=doc["document_id"],
        format="json"
    )
```

**Intelligent Search Workflow:**
```python
# 1. Try exact search first
exact_results = search_documents(
    query='"purchase order 2024-1234"',
    limit=5
)

# 2. If no results, try semantic search
if not exact_results["documents"]:
    semantic_results = vector_search(
        query="purchase order from January 2024 number 1234",
        threshold=0.6
    )

# 3. Analyze found documents
if semantic_results["results"]:
    analysis = analyze_document_content(
        document_id=semantic_results["results"][0]["id"],
        analysis_type="entities"
    )
```

### Batch Operations

**Process Multiple Documents:**
```python
# Upload multiple documents without immediate processing
document_ids = []
for file_path in glob.glob("/path/to/documents/*.pdf"):
    result = upload_document(
        file_path=file_path,
        process_immediately=False
    )
    document_ids.append(result["document_id"])

# Process all at once
process_pending_documents()

# Update embeddings for vector search
update_embeddings()
```

### Search Strategies

**Progressive Search Refinement:**
```python
# Start broad
results = search_documents("contract", limit=50)

# Refine with additional terms
if results["results_count"] > 20:
    results = search_documents("contract AND 2024", limit=20)

# Further refinement
if results["results_count"] > 10:
    results = search_documents(
        'contract AND 2024 AND "payment terms"',
        limit=10
    )
```

---

## Error Handling

### Common Error Responses

**File Not Found:**
```json
{
    "error": "FileNotFoundError",
    "message": "File not found: /path/to/file.pdf",
    "suggestion": "Check file path and permissions"
}
```

**Invalid Parameters:**
```json
{
    "error": "ValidationError",
    "message": "Invalid document_id: must be positive integer",
    "field": "document_id",
    "provided_value": -1
}
```

**Processing Failed:**
```json
{
    "error": "ProcessingError",
    "message": "Failed to extract text from document",
    "document_id": 42,
    "suggestion": "Check if document is corrupted or encrypted"
}
```

### Best Practices

1. **Always Check Status:**
```python
result = upload_document(file_path="document.pdf")
if result.get("status") != "success":
    print(f"Upload failed: {result.get('message')}")
```

2. **Handle Missing Documents:**
```python
try:
    details = get_document_details(document_id=999)
except Exception as e:
    if "not found" in str(e).lower():
        print("Document doesn't exist")
```

3. **Validate Search Queries:**
```python
query = user_input.strip()
if len(query) > 500:
    query = query[:500]  # Truncate to max length
if not query:
    print("Search query cannot be empty")
```

---

## Engine Performance Specifications

**All operations are deterministic** - no variability from AI models.

| Tool | Rate Limit | Max Input Size | Timeout |
|------|------------|----------------|---------|
| upload_document | 10/minute | 50MB file | 60s |
| search_documents | 100/minute | 500 chars | 5s |
| vector_search | 50/minute | 1000 chars | 10s |
| analyze_document_content | 20/minute | - | 30s |
| process_pending_documents | 1/minute | - | 300s |
| update_embeddings | 1/minute | - | 300s |

---

## Integration Examples with Any AI Assistant

**Works with**: Claude Desktop, Microsoft Copilot, or any MCP-compatible client.

### Example 1: Document Upload and Analysis
```
User: "I have an invoice PDF on my desktop. Can you analyze it?"

AI Assistant: I'll help you upload and analyze that invoice. Let me process it for you.

[Calls upload_document with the file path]
[Waits for processing]
[Calls analyze_document_content]

Based on the analysis:
- Invoice Number: INV-2024-1234
- Date: January 15, 2024
- Vendor: Global Supplies Ltd
- Total Amount: $45,750.00
- Payment Terms: NET 30
- Items: 15 line items detected

The invoice contains a table with product details and appears to be for copper materials based on the item descriptions.
```

### Example 2: Intelligent Document Search
```
User: "Find all contracts that mention arbitration clauses"

AI Assistant: I'll search for contracts containing arbitration clauses.

[Calls search_documents with query="contract AND arbitration"]
[If few results, calls vector_search with "legal contracts with dispute resolution arbitration clauses"]

Found 7 contracts with arbitration clauses:
1. Supply_Agreement_2024.pdf - Contains ICC arbitration clause
2. Purchase_Contract_Cu.pdf - Specifies Singapore arbitration
3. Master_Agreement_ACME.pdf - LCIA arbitration rules
...

Would you like me to analyze any of these in detail?
```

---

## Next Steps

- Read the [Usage Guide](USAGE_GUIDE.md) for complete workflows
- Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
- Explore [Architecture](ARCHITECTURE.md) to understand the system
- See [Contributing](CONTRIBUTING.md) to add new features

---

*Need help? Check our [FAQ](TROUBLESHOOTING.md#faq) or [open an issue](https://github.com/kansofy/kansofy-trade/issues)*