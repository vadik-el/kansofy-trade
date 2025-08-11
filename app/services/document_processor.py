"""
Document processing service for Kansofy-Trade using Docling

Extracts text and intelligence from uploaded documents using IBM's Docling.
Supports PDF, DOCX, TXT, XLSX, CSV, PPTX, HTML and more.
"""

import re
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from docling.document_converter import DocumentConverter

from app.core.database import get_db_context
from app.models.document import Document, DocumentStatus, DocumentProcessingLog
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def generate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Generate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read
    
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


class DocumentProcessor:
    """Document processing service with Docling for advanced text extraction"""
    
    def __init__(self):
        # Initialize Docling converter
        self.converter = DocumentConverter()
    
    async def process_document_async(self, document_id: int) -> bool:
        """Process document asynchronously"""
        async with get_db_context() as db:
            return await self.process_document(document_id, db)
    
    async def process_document(self, document_id: int, db: AsyncSession) -> bool:
        """
        Process a document: extract text, analyze content, generate intelligence
        """
        start_time = datetime.utcnow()
        
        # Get document
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        
        if not document:
            logger.error(f"Document {document_id} not found")
            return False
        
        try:
            logger.info(f"Processing document with Docling: {document.filename}")
            
            # Update status
            document.status = DocumentStatus.PROCESSING
            await db.commit()
            
            # Extract text content and tables using Docling
            content, tables = await self._extract_text_and_tables(document.file_path)
            if not content:
                raise Exception("No text content extracted")
            
            # Skip entity extraction and summarization - just save the content
            entities = {}
            summary = ""
            confidence_score = 1.0 if content else 0.0
            
            # Auto-categorize document based on content
            category = self._categorize_document(content, document.filename)
            
            # Generate file hash if not already set
            if not document.file_hash:
                file_path = Path(document.file_path)
                if file_path.exists():
                    document.file_hash = generate_file_hash(file_path)
                    logger.info(f"Generated file hash: {document.file_hash[:8]}...")
            
            # Prepare document metadata for storage
            doc_metadata = {
                "category": category,
                "original_filename": document.original_filename,
                "content_type": document.content_type,
                "file_size": document.file_size,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
            
            # Update document with results
            document.content = content
            document.entities = entities
            document.summary = summary
            document.tables = tables  # Store extracted tables
            document.confidence_score = confidence_score
            document.category = category
            document.doc_metadata = doc_metadata
            document.status = DocumentStatus.COMPLETED
            document.processed_at = datetime.utcnow()
            
            # Generate embeddings for vector search with enhanced JSON storage
            try:
                from app.core.vector_store import generate_document_embeddings
                embedding_result = await generate_document_embeddings(
                    document_id, 
                    content,
                    metadata=doc_metadata
                )
                logger.info(
                    f"Generated {embedding_result['embeddings_count']} embeddings "
                    f"for document {document_id} with hash {embedding_result['document_hash'][:8]}..."
                )
                
                # The full_text_json is already updated in generate_document_embeddings
                
            except Exception as e:
                logger.warning(f"Failed to generate embeddings: {e}")
                # Continue processing even if embeddings fail
            
            # Log successful processing
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            log_entry = DocumentProcessingLog(
                document_id=document_id,
                operation="full_processing",
                status="success",
                message="Document processed successfully with Docling",
                processing_time=processing_time,
                details={
                    "content_length": len(content),
                    "entities_found": len(entities),
                    "confidence_score": confidence_score,
                    "processor": "docling"
                }
            )
            db.add(log_entry)
            
            await db.commit()
            logger.info(f"Document {document_id} processed successfully in {processing_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            
            # Update document status to failed
            document.status = DocumentStatus.FAILED
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log error
            log_entry = DocumentProcessingLog(
                document_id=document_id,
                operation="full_processing",
                status="error",
                message=str(e),
                processing_time=processing_time
            )
            db.add(log_entry)
            
            await db.commit()
            return False
    
    async def _extract_text_and_tables(self, file_path: str) -> Tuple[Optional[str], List[Dict]]:
        """Extract text content and tables from file using Docling"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle plain text files directly (Docling doesn't support them)
        if file_path.suffix.lower() == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Read plain text file directly: {len(content)} characters")
                return content, []  # No tables in plain text
            except Exception as e:
                logger.error(f"Failed to read plain text file {file_path}: {e}")
                raise Exception(f"Plain text file reading failed: {str(e)}")
        
        try:
            # Run Docling conversion in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.converter.convert, 
                str(file_path)
            )
            
            # Export to markdown for rich text preservation
            # This includes tables, lists, headers, and other structure
            markdown_content = result.document.export_to_markdown()
            
            # If markdown is empty, try plain text export
            if not markdown_content or not markdown_content.strip():
                # Fall back to text representation
                text_content = str(result.document)
                content = text_content if text_content.strip() else None
            else:
                content = markdown_content
            
            # Extract tables from the document
            tables = []
            try:
                # Docling provides tables through the document structure
                if hasattr(result.document, 'tables'):
                    for idx, table in enumerate(result.document.tables):
                        # Convert table to a structured format
                        table_data = {
                            "index": idx,
                            "rows": [],
                            "headers": [],
                            "caption": getattr(table, 'caption', None)
                        }
                        
                        # Extract table content - convert TableData to JSON-serializable format
                        if hasattr(table, 'data') and table.data:
                            # table.data is a TableData object, extract its grid
                            if hasattr(table.data, 'grid'):
                                # Convert grid of TableCell objects to simple array of arrays
                                table_rows = []
                                for row in table.data.grid:
                                    row_data = []
                                    for cell in row:
                                        if hasattr(cell, 'text'):
                                            row_data.append(cell.text)
                                        else:
                                            row_data.append(str(cell))
                                    table_rows.append(row_data)
                                table_data["rows"] = table_rows
                                
                                # Try to extract headers from first row if they are marked as headers
                                if table_rows and hasattr(table.data, 'grid') and len(table.data.grid) > 0:
                                    first_row = table.data.grid[0]
                                    if any(hasattr(cell, 'column_header') and cell.column_header for cell in first_row):
                                        table_data["headers"] = table_rows[0]
                                        table_data["rows"] = table_rows[1:]  # Remove header row from data
                                    
                        # Try to get HTML representation if available
                        try:
                            if hasattr(table, 'to_html'):
                                table_data["html"] = table.to_html()
                        except:
                            pass
                        
                        # Try to get CSV representation if available
                        try:
                            if hasattr(table, 'to_csv'):
                                table_data["csv"] = table.to_csv()
                        except:
                            pass
                            
                        tables.append(table_data)
                        logger.info(f"Extracted table {idx} with {len(table_data.get('rows', []))} rows from document")
                
                # Also check for tables in the document elements
                if hasattr(result.document, 'elements'):
                    for element in result.document.elements:
                        if hasattr(element, 'type') and element.type == 'table':
                            table_data = {
                                "index": len(tables),
                                "content": str(element),
                                "type": "element_table"
                            }
                            tables.append(table_data)
                            
            except Exception as e:
                logger.warning(f"Failed to extract tables: {e}")
                # Continue processing even if table extraction fails
            
            logger.info(f"Extracted {len(tables)} tables from document")
            return content, tables
            
        except Exception as e:
            logger.error(f"Docling extraction failed for {file_path}: {e}")
            raise Exception(f"Document extraction failed: {str(e)}")
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract key entities from document content"""
        entities = {
            "amounts": [],
            "dates": [],
            "companies": [],
            "products": [],
            "references": [],
            "emails": [],
            "phone_numbers": []
        }
        
        # Amount patterns (currency amounts)
        amount_patterns = [
            r'\$[\d,]+\.?\d*',  # USD amounts
            r'€[\d,]+\.?\d*',   # EUR amounts  
            r'£[\d,]+\.?\d*',   # GBP amounts
            r'USD\s*[\d,]+\.?\d*',
            r'EUR\s*[\d,]+\.?\d*',
            r'[\d,]+\.\d{2}\s*USD',
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities["amounts"].extend(matches)
        
        # Date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{2}-\d{2}',      # YYYY-MM-DD
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # DD Mon YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities["dates"].extend(matches)
        
        # Company patterns (common trading company patterns)
        company_patterns = [
            r'\b[A-Z][a-zA-Z\s]+(?:Ltd|Inc|Corp|LLC|AG|plc|GmbH)\b',
            r'\b[A-Z][a-zA-Z\s]+(?:Limited|Incorporated|Corporation)\b',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, content)
            entities["companies"].extend(matches)
        
        # Product patterns (metals and commodities)
        product_keywords = [
            'copper', 'aluminum', 'zinc', 'lead', 'nickel', 'tin',
            'concentrate', 'cathode', 'wire rod', 'ingot', 'billet'
        ]
        
        for keyword in product_keywords:
            if keyword.lower() in content.lower():
                entities["products"].append(keyword.title())
        
        # Reference numbers (invoice, PO, contract numbers)
        reference_patterns = [
            r'\b(?:INV|PO|CONTRACT)[-\s]*\d+\b',
            r'\b[A-Z]{2,4}[-\s]*\d{4,}\b',
        ]
        
        for pattern in reference_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities["references"].extend(matches)
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, content)
        
        # Phone numbers
        phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'
        entities["phone_numbers"] = re.findall(phone_pattern, content)
        
        # Remove duplicates and limit results
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]  # Max 10 per category
        
        return entities
    
    def _generate_summary(self, content: str) -> str:
        """Generate a basic summary of document content"""
        # Simple extractive summary - take first few sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter out very short sentences
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Take first 3 meaningful sentences
        summary_sentences = meaningful_sentences[:3]
        
        if not summary_sentences:
            return "Document content appears to be structured data or very brief text."
        
        summary = ". ".join(summary_sentences)
        
        # Ensure summary ends properly
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _categorize_document(self, content: str, filename: str) -> str:
        """Auto-categorize document based on content and filename"""
        content_lower = content.lower() if content else ""
        filename_lower = filename.lower() if filename else ""
        
        # Category keywords mapping
        categories = {
            "invoice": ["invoice", "bill", "payment due", "invoice number", "invoice date"],
            "contract": ["agreement", "contract", "parties", "terms and conditions", "whereas"],
            "shipping": ["bill of lading", "vessel", "cargo", "shipment", "container", "port"],
            "inspection": ["inspection", "inspection report", "quality", "certificate", "compliance"],
            "purchase_order": ["purchase order", "po number", "delivery date", "quantity ordered"],
            "report": ["report", "analysis", "findings", "executive summary", "conclusion"],
            "financial": ["balance", "statement", "transaction", "account", "credit", "debit"],
            "correspondence": ["dear", "sincerely", "regards", "letter", "memo", "email"]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += content_lower.count(keyword)
                if keyword in filename_lower:
                    score += 5  # Filename matches are weighted higher
            category_scores[category] = score
        
        # Return the category with highest score, or "other" if no matches
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0]
        
        return "other"
    
    def _calculate_confidence(self, content: str, entities: Dict[str, List[str]]) -> float:
        """Calculate processing confidence score based on content analysis"""
        confidence = 0.0
        
        # Base confidence for successful text extraction
        if content and len(content.strip()) > 0:
            confidence += 0.3
        
        # Content length factor
        if len(content) > 100:
            confidence += 0.2
        if len(content) > 1000:
            confidence += 0.1
        
        # Entity extraction factor
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities > 0:
            confidence += 0.2
        if total_entities > 5:
            confidence += 0.1
        if total_entities > 10:
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0