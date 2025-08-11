# Document Upload via Claude Desktop

## ✅ Feature Implemented

You can now upload documents directly through Claude Desktop using the MCP server integration!

## How to Use

### Option 1: Upload Local Files
If you have a file on your computer, you can upload it by providing the file path:

```
Use the upload_document tool with:
- file_path: "/path/to/your/document.pdf"
- category: "contract" (or invoice, report, email, presentation, other)
- process_immediately: true (to extract text and enable search)
```

### Option 2: Upload Base64 Content
For files that Claude has access to (like files you've shared), you can upload using base64 encoding:

```
Use the upload_document tool with:
- base64_content: [base64 encoded file data]
- filename: "document.pdf"
- category: "invoice"
- process_immediately: true
```

## Supported File Types

- **PDF** - Portable Document Format
- **DOCX** - Microsoft Word documents
- **TXT** - Plain text files
- **XLSX** - Microsoft Excel spreadsheets
- **CSV** - Comma-separated values

## Features

### Automatic Processing
- **Text extraction** from PDFs and documents
- **Table extraction** from structured documents
- **Vector embeddings** for semantic search
- **Duplicate detection** using SHA-256 hashing
- **Full-text search** indexing

### Size Limits
- Maximum file size: **50 MB**
- No limit on number of documents

### Duplicate Prevention
The system automatically detects duplicate documents using content hashing. If you try to upload the same document twice, it will notify you and show the existing document ID.

## Available Tools (12 total)

1. **upload_document** - Upload new documents 📤
2. **search_documents** - Full-text search across all documents
3. **get_document_details** - Get detailed information about a specific document
4. **get_document_statistics** - View system-wide statistics
5. **analyze_document_content** - Analyze content patterns and entities
6. **get_system_health** - Check system health status
7. **vector_search** - Semantic similarity search
8. **find_duplicates** - Find similar documents
9. **update_embeddings** - Generate/update vector embeddings
10. **get_document_json** - Extract full JSON representation
11. **check_duplicate_by_hash** - Check for exact duplicates
12. **get_document_tables** - Extract tables from documents

## Example Upload Session

```
User: "Upload the contract at /Users/john/Documents/contract.pdf"

Claude: [Uses upload_document tool]

Response:
✅ Document Uploaded and Processed Successfully

- Document ID: 6
- Filename: contract.pdf
- Size: 245.3 KB
- Type: PDF
- Category: contract
- Status: completed
- Hash: a3f5d8e2b9c1d4e6...

📝 Document has been processed and is ready for search and analysis.
```

## Processing Status

Documents go through these stages:
1. **uploaded** - File saved to system
2. **pending** - Queued for processing
3. **processing** - Text extraction in progress
4. **completed** - Ready for search and analysis
5. **failed** - Processing error (can be retried)

## Security Features

- **Content hashing** - SHA-256 for integrity
- **Safe filenames** - UUID-based naming prevents conflicts
- **Type validation** - Only allowed file types accepted
- **Size limits** - Prevents resource exhaustion
- **Duplicate detection** - Saves storage and processing

## Next Steps

After uploading documents, you can:
- Search for specific content using `search_documents`
- Find similar documents using `vector_search`
- Extract tables using `get_document_tables`
- Analyze content patterns using `analyze_document_content`
- Check for duplicates using `find_duplicates`

The system is now fully operational with document upload capabilities through Claude Desktop!