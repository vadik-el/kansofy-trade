"""
Document management endpoints for Kansofy-Trade

Handles document upload, retrieval, and management operations.
"""

import os
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form,
    Query, BackgroundTasks
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.core.config import get_settings
from app.models.document import (
    Document, DocumentResponse, DocumentCreate, DocumentUpdate,
    DocumentStats, DocumentStatus
)
from app.services.document_processor import DocumentProcessor

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


def get_document_processor():
    """Dependency to get document processor instance"""
    return DocumentProcessor()


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Upload a new document for processing.
    
    Supports: PDF, DOCX, TXT, XLSX, CSV files up to 50MB.
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in settings.get_allowed_extensions_set():
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not supported. Allowed: {settings.allowed_extensions}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
        )
    
    # Calculate file hash for deduplication
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check for duplicate
    existing_doc = await db.execute(
        select(Document).where(Document.file_hash == file_hash)
    )
    if existing_doc.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Document with identical content already exists"
        )
    
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = settings.upload_path / safe_filename
        
        # Ensure upload directory exists
        settings.upload_path.mkdir(exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            import json
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid metadata JSON: {metadata}")
        
        # Create document record
        document_data = DocumentCreate(
            filename=safe_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            file_hash=file_hash,
            content_type=file.content_type,
            metadata=doc_metadata
        )
        
        db_document = Document(**document_data.model_dump())
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)
        
        # Queue for background processing
        background_tasks.add_task(
            processor.process_document_async, 
            db_document.id
        )
        
        logger.info(f"Document uploaded successfully: {file.filename} (ID: {db_document.id})")
        
        # Refresh object to get all computed fields
        await db.refresh(db_document)
        return DocumentResponse(**db_document.to_dict())
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        # Clean up file if database operation failed
        if 'file_path' in locals() and Path(file_path).exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of documents"),
    status: Optional[DocumentStatus] = Query(None, description="Filter by status"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    db: AsyncSession = Depends(get_db)
):
    """List documents with optional filtering and pagination."""
    
    query = select(Document).order_by(desc(Document.uploaded_at))
    
    # Apply filters
    if status:
        query = query.where(Document.status == status)
    if content_type:
        query = query.where(Document.content_type.like(f"%{content_type}%"))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [DocumentResponse(**doc.to_dict()) for doc in documents]


@router.get("/documents/stats", response_model=DocumentStats)
async def get_document_statistics(db: AsyncSession = Depends(get_db)):
    """Get document statistics and analytics."""
    
    # Total documents
    total_result = await db.execute(select(func.count(Document.id)))
    total_documents = total_result.scalar()
    
    # By status
    status_result = await db.execute(
        select(Document.status, func.count(Document.id))
        .group_by(Document.status)
    )
    by_status = {status: count for status, count in status_result.fetchall()}
    
    # By content type
    content_type_result = await db.execute(
        select(Document.content_type, func.count(Document.id))
        .where(Document.content_type.is_not(None))
        .group_by(Document.content_type)
    )
    by_content_type = {ct: count for ct, count in content_type_result.fetchall()}
    
    # Total size
    size_result = await db.execute(select(func.sum(Document.file_size)))
    total_size = size_result.scalar() or 0
    
    # Average confidence score
    confidence_result = await db.execute(
        select(func.avg(Document.confidence_score))
        .where(Document.confidence_score > 0)
    )
    avg_confidence = confidence_result.scalar() or 0.0
    
    # Recent uploads (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(days=1)
    recent_result = await db.execute(
        select(func.count(Document.id))
        .where(Document.uploaded_at >= recent_cutoff)
    )
    recent_uploads = recent_result.scalar()
    
    return DocumentStats(
        total_documents=total_documents,
        by_status=by_status,
        by_content_type=by_content_type,
        total_size=total_size,
        avg_confidence_score=round(avg_confidence, 3),
        recent_uploads=recent_uploads
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document by ID."""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(**document.to_dict())


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata and status."""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update fields
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    document.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse(**document.to_dict())


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its file."""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from storage
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Could not delete file {document.file_path}: {e}")
    
    # Delete from database
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}


@router.post("/documents/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """Manually trigger document processing."""
    
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Process document synchronously for immediate results
    try:
        success = await processor.process_document(document_id, db)
        if not success:
            raise HTTPException(status_code=500, detail="Processing failed")
        
        # Return updated document
        await db.refresh(document)
        return DocumentResponse(**document.to_dict())
        
    except Exception as e:
        logger.error(f"Manual processing failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")