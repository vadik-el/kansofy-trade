"""
Document models for Kansofy-Trade

SQLAlchemy models for document storage and metadata management.
Designed for simplicity and fast full-text search with SQLite FTS5.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from sqlalchemy import (
    Column, String, DateTime, Integer, Float, Text, Boolean, 
    ForeignKey, Index, event, JSON
)
from sqlalchemy.orm import relationship, validates
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import Base


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Document(Base):
    """Document model with full-text search support"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100))
    file_hash = Column(String(64), index=True)  # SHA-256 hash for deduplication
    
    # Document categorization
    category = Column(String(50), index=True)  # invoice, contract, report, shipping, etc.
    
    # Processing information
    status = Column(String(20), default=DocumentStatus.UPLOADED, index=True)
    content = Column(Text)  # Extracted text content
    doc_metadata = Column(JSON)  # Document metadata as JSON
    
    # Full document data as JSON (includes text, chunks, metadata, embeddings)
    full_text_json = Column(JSON)  # Complete document data in JSON format
    
    # Intelligence extracted data
    entities = Column(JSON)  # Extracted entities (names, amounts, dates, etc.)
    summary = Column(Text)   # Document summary
    tables = Column(JSON)    # Extracted tables from document
    confidence_score = Column(Float, default=0.0)  # Processing confidence (0-1)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    processing_logs = relationship("DocumentProcessingLog", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_document_status_uploaded', 'status', 'uploaded_at'),
        Index('idx_document_filename', 'filename'),
        Index('idx_document_content_type', 'content_type'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in [s.value for s in DocumentStatus]:
            raise ValueError(f"Invalid status: {status}")
        return status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'status': self.status,
            'confidence_score': self.confidence_score,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.doc_metadata,
            'entities': self.entities,
            'has_content': bool(self.content),
            'content_length': len(self.content) if self.content else 0,
            # Include the actual content and summary
            'content': self.content,
            'summary': self.summary,
            'tables': self.tables,
        }


class DocumentProcessingLog(Base):
    """Processing log for document operations"""
    __tablename__ = "document_processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    
    # Processing details
    operation = Column(String(50), nullable=False)  # extract_text, analyze, etc.
    status = Column(String(20), nullable=False)     # success, error, warning
    message = Column(Text)
    details = Column(JSON)  # Additional processing details
    
    # Performance metrics
    processing_time = Column(Float)  # Processing time in seconds
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relations
    document = relationship("Document", back_populates="processing_logs")
    
    __table_args__ = (
        Index('idx_processing_log_document_status', 'document_id', 'status'),
    )


# Pydantic models for API
class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    original_filename: str
    file_path: str
    file_size: int
    file_hash: str


class DocumentUpdate(BaseModel):
    """Document update schema"""
    status: Optional[DocumentStatus] = None
    content: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentBase):
    """Document response schema"""
    id: int
    uuid: str
    original_filename: str
    file_size: int
    status: DocumentStatus
    confidence_score: float
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    updated_at: datetime
    has_content: bool
    content_length: int
    # Include the actual content fields
    content: Optional[str] = None
    entities: Optional[Union[str, Dict[str, Any]]] = None
    summary: Optional[str] = None
    tables: Optional[Union[str, List[Dict[str, Any]]]] = None
    
    model_config = ConfigDict(from_attributes=True)


class DocumentSearchResult(BaseModel):
    """Document search result schema"""
    id: int
    filename: str
    file_size: int
    uploaded_at: datetime
    content_type: Optional[str]
    snippet: str
    relevance_score: float
    
    model_config = ConfigDict(from_attributes=True)


class DocumentStats(BaseModel):
    """Document statistics schema"""
    total_documents: int
    by_status: Dict[str, int]
    by_content_type: Dict[str, int]
    total_size: int
    avg_confidence_score: float
    recent_uploads: int  # Last 24 hours
    
    model_config = ConfigDict(from_attributes=True)