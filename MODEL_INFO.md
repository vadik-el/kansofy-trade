# Local AI Model Documentation

## Overview

TradeMCP uses a **100% local AI model** for intelligent document processing. This means all AI processing happens on your machine - no cloud services, no API calls, no data leaving your computer.

## The Model: all-MiniLM-L6-v2

### Technical Specifications

- **Full Name**: `sentence-transformers/all-MiniLM-L6-v2`
- **Type**: Sentence embedding model (transformer-based)
- **Size**: ~87MB (90,868,376 bytes exactly)
- **Architecture**: BERT-based, 6 layers, 384 dimensions
- **Performance**: 
  - Embedding speed: ~14,200 sentences/second on CPU
  - ~2800x faster than BERT-base
  - Quality: 80% of BERT-base performance at 5% of the size
- **Hardware Requirements**:
  - Runs on CPU (no GPU required)
  - ~200MB RAM when loaded
  - Works on any modern computer

### What Are Embeddings?

Embeddings are numerical representations of text that capture meaning:
- Converts text → 384-dimensional vectors
- Similar meanings = similar vectors
- Enables semantic search and comparison

### How It Works in TradeMCP

```python
# Example: Finding similar trade documents
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert documents to embeddings
doc1 = "Purchase order for 1000 units of steel"
doc2 = "Order confirmation: 1000 steel units"
doc3 = "Invoice for office supplies"

embeddings = model.encode([doc1, doc2, doc3])

# Documents 1 and 2 will have similar embeddings
# Document 3 will be different
```

## Use Cases in Trade Document Processing

### 1. **Semantic Document Search**
Instead of exact keyword matching:
- Search: "purchase agreements"
- Finds: "PO", "buying contract", "procurement deal"

### 2. **Document Classification**
Automatically categorize documents:
- Purchase Orders → Procurement folder
- Bills of Lading → Shipping folder
- Invoices → Finance folder

### 3. **Duplicate Detection**
Find similar documents even with different wording:
- "Invoice #123" ≈ "Bill #123"
- "P.O. 456" ≈ "Purchase Order 456"

### 4. **Information Extraction**
Understand context for better extraction:
- Recognizes "buyer" vs "seller" from context
- Identifies related line items across documents

### 5. **Document Validation**
Check if documents match expected patterns:
- Verify PO matches invoice
- Ensure shipping docs align with orders

## Privacy & Security

### 100% Local Processing
- **No Internet Required**: Works completely offline
- **No API Keys**: No OpenAI, Google, or cloud service accounts
- **No Data Transmission**: Documents never leave your machine
- **No Usage Tracking**: No telemetry or usage analytics

### Data Flow
```
Your Document → Local Model → Embeddings → Analysis → Results
     ↑                                                    ↓
     └────────── All on your machine ────────────────────┘
```

### Security Benefits
- **Trade Secrets Safe**: Sensitive commercial data stays private
- **Compliance**: Meets data residency requirements
- **No Vendor Lock-in**: Not dependent on external services
- **Predictable Costs**: No per-document or per-API-call charges

## Performance Characteristics

### Speed
- **Embedding Generation**: ~0.07ms per sentence
- **Document Comparison**: <1ms for 1000 documents
- **No Network Latency**: Instant processing

### Accuracy
- **Multilingual**: Supports 100+ languages
- **Domain Agnostic**: Works with any document type
- **Consistent Results**: Deterministic outputs

### Resource Usage
- **CPU**: Low usage, runs on standard processors
- **Memory**: ~200MB when active
- **Disk**: 87MB storage
- **GPU**: Optional, not required

## Comparison with Cloud Models

| Feature | Local Model (MiniLM) | Cloud APIs (GPT, Claude) |
|---------|---------------------|-------------------------|
| Privacy | 100% local | Data sent to servers |
| Cost | Free after download | Per-token charges |
| Speed | Instant | Network latency |
| Internet | Not required | Required |
| API Keys | None | Required |
| Rate Limits | None | Yes |
| Consistency | Deterministic | May vary |
| Document Security | Complete | Depends on provider |

## Technical Integration

### Loading the Model
```python
from sentence_transformers import SentenceTransformer

# Load from local cache
model = SentenceTransformer(
    'sentence-transformers/all-MiniLM-L6-v2',
    cache_folder='model_cache'
)
```

### Generating Embeddings
```python
# Single document
embedding = model.encode("Purchase order document text")

# Multiple documents (batch processing)
embeddings = model.encode([
    "Document 1 text",
    "Document 2 text",
    "Document 3 text"
])
```

### Finding Similar Documents
```python
from sklearn.metrics.pairwise import cosine_similarity

# Calculate similarity between documents
similarity_scores = cosine_similarity(embeddings)

# Find most similar documents
similar_indices = similarity_scores.argsort()[::-1]
```

## Model Management

### Storage Location
- Path: `model_cache/models--sentence-transformers--all-MiniLM-L6-v2/`
- Persistent between sessions
- Excluded from git repository

### Updating the Model
The model is stable and doesn't require updates. If needed:
```bash
rm -rf model_cache/
python download_models.py
```

### Troubleshooting

**Model not downloading?**
- Check internet connection (one-time download)
- Ensure 100MB free disk space
- Verify Python dependencies installed

**Performance issues?**
- Close other heavy applications
- Consider batch processing for many documents
- Use GPU if available (optional)

## Alternative Models

While MiniLM-L6-v2 is optimal for most use cases, alternatives exist:

- **Larger/More Accurate**: `all-mpnet-base-v2` (420MB)
- **Smaller/Faster**: `all-MiniLM-L12-v2` (120MB)
- **Multilingual Focus**: `paraphrase-multilingual-MiniLM-L12-v2`

To use a different model, modify `download_models.py`.

## Conclusion

The local AI model provides intelligent document processing while maintaining:
- Complete privacy and security
- Zero operational costs
- Consistent, reliable performance
- No external dependencies

Perfect for trade document processing where data sensitivity and reliability are paramount.