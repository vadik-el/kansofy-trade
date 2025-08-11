# Contributing to the Engine 🤝

**Building the deterministic infrastructure for document workflows. No AI required.**

Thank you for contributing to TradeMCP! This is the **engine** layer - deterministic document operations that work the same every time.

## Table of Contents
- [Engine vs Brain: Contribution Boundaries](#engine-vs-brain-contribution-boundaries)
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Architecture Guidelines](#architecture-guidelines)
- [Adding New Features](#adding-new-features)
- [Documentation](#documentation)
- [Community](#community)

## Engine vs Brain: Contribution Boundaries

### What Belongs in the Engine (This Project)

✅ **Engine Contributions (Welcome Here)**:
- **Deterministic Operations**: Same input → same output, always
- **Document Processing**: Docling extraction, parsing, formatting
- **Search Infrastructure**: SQL queries, FTS5 optimization, vector math
- **MCP Protocol**: Tool definitions, protocol handling, response formatting
- **Storage & Retrieval**: Database schemas, file handling, caching
- **Performance**: Query optimization, batch processing, parallelization
- **Rule-Based Logic**: Regex patterns, validation rules, deterministic scoring

**Examples of Good Engine Contributions**:
```python
# ✅ Deterministic entity extraction
def extract_invoice_number(text: str) -> str:
    pattern = r'Invoice[\s#:]*([A-Z0-9-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

# ✅ SQL-based search
def search_by_date_range(start: date, end: date):
    return db.query("SELECT * FROM documents WHERE date BETWEEN ? AND ?", start, end)

# ✅ Pre-computed similarity
def find_similar(embedding: list[float], threshold: float = 0.8):
    # Pure math - cosine similarity on pre-computed vectors
    return cosine_similarity(embedding, stored_embeddings)
```

### What Belongs in the Brain (Not Here)

❌ **Brain Contributions (Use Your Own AI)**:
- **AI/ML Models**: Training, inference, fine-tuning
- **Natural Language Understanding**: Intent detection, sentiment analysis
- **Decision Making**: Workflow orchestration, business logic
- **Content Generation**: Summaries, responses, translations
- **OCR/Vision**: Image processing, handwriting recognition
- **Predictions**: Forecasting, classification, recommendations

**Examples to Avoid**:
```python
# ❌ Don't add AI inference
def classify_document(text):
    # This uses AI - belongs in brain layer
    return openai.classify(text)

# ❌ Don't add decision logic  
def should_approve_invoice(invoice):
    # Business logic - belongs in brain
    if invoice.amount > threshold:
        return requires_manager_approval()

# ❌ Don't add content generation
def summarize_document(text):
    # AI generation - belongs in brain
    return llm.generate_summary(text)
```

### The Line Between Engine and Brain

| Operation | Engine (Here) | Brain (Not Here) |
|-----------|--------------|------------------|
| Extract tables | Docling rules ✅ | Understand table meaning ❌ |
| Find invoices | SQL search ✅ | Decide which to pay ❌ |
| Match patterns | Regex ✅ | Understand context ❌ |
| Calculate similarity | Vector math ✅ | Judge relevance ❌ |
| Store documents | Database ✅ | Categorize by meaning ❌ |
| Parse dates | Pattern matching ✅ | Understand urgency ❌ |

### Why This Separation Matters

1. **Determinism**: Engine always produces same results
2. **No AI Dependencies**: Runs without API keys or models
3. **Vendor Agnostic**: Works with any AI layer
4. **Predictable Costs**: No per-token charges
5. **Offline Capable**: Everything works locally

### Contributing Philosophy

**Engine Philosophy**: "Can this be solved with rules, patterns, or math?"
- If YES → Contribute here
- If NO (needs AI) → Implement in your brain layer

**Questions to Ask**:
1. Will this operation always produce the same output for the same input?
2. Can this be implemented without ML models or AI inference?
3. Does this work offline without API calls?
4. Is this about infrastructure rather than intelligence?

If you answered YES to all → Perfect engine contribution!

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that could be considered inappropriate

## How to Contribute

### Types of Contributions

We welcome engine-layer contributions:

- 🐛 **Bug Reports**: Help us identify and fix deterministic issues
- ✨ **Feature Requests**: Suggest new engine capabilities (no AI)
- 📚 **Documentation**: Improve guides and API docs
- 🔧 **Code Contributions**: Submit deterministic fixes and features
- 🧪 **Testing**: Add test coverage for predictable operations
- 🎨 **UI/UX Improvements**: Enhance the web interface
- 🌍 **Translations**: Help internationalize the project
- ⚡ **Performance**: Optimize queries, caching, batch processing
- 🔍 **Search**: Improve FTS5, vector math, SQL optimization

### First Time Contributors

Look for issues tagged with:
- `good first issue` - Simple tasks perfect for beginners
- `help wanted` - Tasks where we need community help
- `documentation` - Documentation improvements

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/trademcp.git
cd trademcp

# Add upstream remote
git remote add upstream https://github.com/kansofy/trademcp.git
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv-dev
source venv-dev/bin/activate  # On Windows: venv-dev\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Install Development Tools

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install testing tools
pip install pytest pytest-asyncio pytest-cov
pip install black isort flake8 mypy

# Install documentation tools
pip install mkdocs mkdocs-material
```

### 4. Set Up Development Database

```bash
# Initialize test database
cp kansofy_trade.db kansofy_trade_dev.db

# Set environment variable
export DATABASE_PATH=./kansofy_trade_dev.db
```

### 5. Run Development Server

```bash
# Start with hot reload
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, start MCP server
python mcp_server.py --debug
```

## Code Standards

### Python Style Guide

We follow PEP 8 with these specifics:

```python
# File structure
"""
Module docstring explaining purpose and usage.
"""

import standard_library
import third_party

from app.local import modules


# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class DocumentProcessor:
    """
    Class docstring with description.
    
    Attributes:
        attribute_name: Description of attribute
    """
    
    def process_document(self, document: Document) -> ProcessedDocument:
        """
        Method docstring with description.
        
        Args:
            document: The document to process
            
        Returns:
            ProcessedDocument: The processed result
            
        Raises:
            ProcessingError: If processing fails
        """
        # Implementation
        pass
```

### Code Quality Tools

Run these before committing:

```bash
# Format code
black app/ tests/
isort app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/

# All checks
pre-commit run --all-files
```

### Naming Conventions

```python
# Variables and functions: snake_case
document_id = 42
def process_document():
    pass

# Classes: PascalCase
class DocumentProcessor:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_UPLOAD_SIZE = 52428800

# Private methods/attributes: leading underscore
def _internal_method():
    pass

# File names: snake_case
document_processor.py
```

### Error Handling

```python
# Always use specific exceptions
class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""
    pass

# Provide context in errors
def get_document(document_id: int) -> Document:
    try:
        document = db.query(Document).filter_by(id=document_id).first()
        if not document:
            raise DocumentNotFoundError(
                f"Document with ID {document_id} not found"
            )
        return document
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching document {document_id}: {e}")
        raise DatabaseError(f"Failed to fetch document: {str(e)}")

# Always log errors
logger.error(f"Processing failed for document {doc_id}: {error}")
```

## Testing Requirements

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
├── e2e/           # End-to-end tests for complete workflows
└── fixtures/      # Test data and fixtures
```

### Writing Tests

```python
# test_document_processor.py
import pytest
from app.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a processor instance for testing."""
        return DocumentProcessor()
    
    @pytest.fixture
    def sample_document(self, tmp_path):
        """Create a sample document for testing."""
        doc_path = tmp_path / "test.txt"
        doc_path.write_text("Test content")
        return str(doc_path)
    
    def test_process_text_document(self, processor, sample_document):
        """Test processing a simple text document."""
        # Arrange
        expected_length = 12  # "Test content"
        
        # Act
        result = processor.process_document(sample_document)
        
        # Assert
        assert result.status == "completed"
        assert len(result.content) == expected_length
        assert result.confidence_score > 0.9
    
    @pytest.mark.asyncio
    async def test_async_processing(self, processor, sample_document):
        """Test asynchronous document processing."""
        result = await processor.process_async(sample_document)
        assert result.status == "completed"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_document_processor.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "not slow"
```

### Test Coverage Requirements

- New features must have >80% test coverage
- Critical paths must have >95% coverage
- All API endpoints must have integration tests
- All MCP tools must have end-to-end tests

## Pull Request Process

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# Or for bugs:
git checkout -b fix/issue-description
```

### 2. Make Changes

```bash
# Make your changes
# Add tests
# Update documentation

# Commit with descriptive message
git add .
git commit -m "feat: add semantic search capability

- Implement vector embeddings
- Add similarity search endpoint
- Update documentation
- Add comprehensive tests

Closes #123"
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```bash
feat(search): add vector similarity search
fix(upload): handle large PDF files correctly
docs(api): update MCP tools documentation
test(processor): add table extraction tests
```

### 3. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### 4. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- List specific changes
- Include relevant details

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Commits are descriptive

## Related Issues
Closes #issue_number

## Screenshots (if applicable)
Add screenshots for UI changes
```

### 5. Review Process

1. **Automated Checks**: CI runs tests, linting, coverage
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Get approval from maintainer
5. **Merge**: Maintainer merges to main

## Architecture Guidelines

### Maintaining Engine Determinism

**Every contribution must maintain determinism:**
```python
# ✅ GOOD: Deterministic
def calculate_document_score(doc):
    score = 0
    if doc.has_tables: score += 0.2
    if doc.has_entities: score += 0.3
    if len(doc.text) > 1000: score += 0.5
    return score  # Always same score for same doc

# ❌ BAD: Non-deterministic
def calculate_document_score(doc):
    score = random.random()  # Random!
    if datetime.now().hour > 12: score += 0.5  # Time-dependent!
    score += ai_quality_check(doc)  # AI-dependent!
    return score
```

### Adding New MCP Tools

1. **Define tool in `mcp_server.py`:**
```python
Tool(
    name="your_tool_name",
    description="Clear description of what the tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
```

2. **Implement handler:**
```python
async def your_tool_handler(arguments: dict) -> list[TextContent]:
    """Handle your_tool_name execution."""
    param1 = arguments.get("param1")
    
    try:
        # Tool logic here
        result = perform_operation(param1)
        
        return [TextContent(
            type="text",
            text=f"Success: {result}"
        )]
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
```

3. **Add to router:**
```python
elif name == "your_tool_name":
    return await your_tool_handler(arguments)
```

4. **Add tests:**
```python
def test_your_tool():
    result = await your_tool_handler({"param1": "value"})
    assert "Success" in result[0].text
```

5. **Update documentation** in `MCP_TOOLS_REFERENCE.md`

### Adding New Document Processors

1. **Create processor class:**
```python
# app/services/processors/your_processor.py
from app.services.base_processor import BaseProcessor

class YourFormatProcessor(BaseProcessor):
    """Process YOUR_FORMAT documents."""
    
    supported_formats = ['.your_ext']
    
    def extract_content(self, file_path: str) -> dict:
        """Extract content from YOUR_FORMAT file."""
        # Implementation
        return {
            'text': extracted_text,
            'metadata': metadata,
            'tables': tables
        }
```

2. **Register processor:**
```python
# In document_processor.py
PROCESSORS = {
    '.your_ext': YourFormatProcessor(),
    # ...
}
```

3. **Add tests and documentation**

## Adding New Features

### Feature Development Process

1. **Discuss First**: Open an issue to discuss the feature
2. **Verify Engine Scope**: Confirm it's deterministic (no AI needed)
3. **Design Document**: For major features, create a design doc
4. **Prototype**: Build a minimal working version
5. **Tests**: Write comprehensive tests (must be deterministic)
6. **Documentation**: Update all relevant docs
7. **Performance**: Ensure no regression
8. **Security**: Consider security implications
9. **Determinism Check**: Verify same input → same output

### Feature Checklist

- [ ] **Is deterministic** (same input → same output)
- [ ] **No AI required** (no models, no inference)
- [ ] **Works offline** (no external API calls)
- [ ] Follows existing architecture patterns
- [ ] Includes unit tests (>80% coverage)
- [ ] Includes integration tests
- [ ] Updates API documentation
- [ ] Updates user documentation
- [ ] Considers backward compatibility
- [ ] Handles errors gracefully
- [ ] Logs appropriately
- [ ] Performance impact assessed
- [ ] Security implications considered

## Documentation

### Documentation Requirements

All contributions must include:

1. **Code Documentation**:
   - Docstrings for all public functions/classes
   - Inline comments for complex logic
   - Type hints for all parameters

2. **User Documentation**:
   - Update README if needed
   - Update relevant guides
   - Add examples

3. **API Documentation**:
   - Update API reference
   - Include request/response examples
   - Document error cases

### Documentation Style

```python
def process_document(
    file_path: str,
    category: str = "other",
    process_immediately: bool = True
) -> Dict[str, Any]:
    """
    Process a document for intelligence extraction.
    
    This function handles the complete document processing pipeline,
    including text extraction, entity recognition, and indexing.
    
    Args:
        file_path: Path to the document file
        category: Document category (invoice, contract, etc.)
        process_immediately: Whether to process immediately or queue
    
    Returns:
        Dictionary containing:
            - document_id: Unique identifier
            - status: Processing status
            - extracted_data: Extracted information
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ProcessingError: If processing fails
        ValueError: If category is invalid
    
    Example:
        >>> result = process_document("/path/to/invoice.pdf", "invoice")
        >>> print(f"Document ID: {result['document_id']}")
        42
    """
    # Implementation
    pass
```

## Community

### Getting Help

- **Discord**: [Join our Discord](https://discord.gg/kansofy)
- **Discussions**: [GitHub Discussions](https://github.com/kansofy/trademcp/discussions)
- **Issues**: [GitHub Issues](https://github.com/kansofy/trademcp/issues)

### Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Release notes
- Project README

### Becoming a Maintainer

Active contributors who demonstrate:
- Consistent quality contributions
- Good understanding of the codebase
- Helpful community participation
- Alignment with project goals

May be invited to become maintainers.

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes drafted
- [ ] Tagged in git
- [ ] Published to PyPI

---

## Thank You! 🙏

Your contributions make TradeMCP better for everyone. We appreciate your time and effort!

**Happy Contributing!** 🚀

---

*Questions? Reach out in [Discussions](https://github.com/kansofy/trademcp/discussions) or [Discord](https://discord.gg/kansofy)*