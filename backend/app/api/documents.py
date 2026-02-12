"""
Document upload and management API endpoints.
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional
import logging
import aiofiles

from app.config import get_settings, ensure_directories
from app.models import (
    DocumentUploadResponse, 
    DocumentInfo, 
    DocumentCategory
)
from app.ingestion.pipeline import IngestionPipeline
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: DocumentCategory = Form(DocumentCategory.OTHER),
    uploaded_by: Optional[str] = Form(None)
):
    """
    Upload a document for processing.
    
    The document will be:
    1. Saved to disk
    2. Text extracted
    3. Split into chunks
    4. Embedded and stored in vector database
    """
    settings = get_settings()
    ensure_directories()
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {ALLOWED_EXTENSIONS}"
        )
    
    # Save file to disk
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Process the document
        pipeline = IngestionPipeline()
        result = pipeline.ingest_document(
            file_path=file_path,
            filename=file.filename,
            category=category,
            uploaded_by=uploaded_by
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DocumentInfo])
async def list_documents(
    category: Optional[DocumentCategory] = Query(None)
):
    """
    List all uploaded documents.
    
    Optionally filter by category.
    """
    try:
        vector_store = VectorStoreService()
        documents = vector_store.get_unique_documents()
        
        # Filter by category if specified
        if category:
            documents = [
                d for d in documents 
                if d.get("category") == category.value
            ]
        
        # Convert to DocumentInfo
        result = []
        settings = get_settings()
        
        for doc in documents:
            doc_name = doc.get("document_name", "")
            file_path = os.path.join(settings.upload_dir, doc_name)
            
            file_size = 0
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
            
            result.append(DocumentInfo(
                id=doc.get("id", ""),
                filename=doc_name,
                category=DocumentCategory(doc.get("category", "other")),
                page_count=0,  # Would need to track this
                chunk_count=0,  # Would need to count from vector store
                file_size=file_size,
                uploaded_at=doc.get("uploaded_at", ""),
                uploaded_by=doc.get("uploaded_by")
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its vectors.
    """
    try:
        pipeline = IngestionPipeline()
        pipeline.delete_document(document_id)
        
        return {"status": "success", "message": f"Document {document_id} deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """
    Get available document categories.
    """
    return [
        {"value": cat.value, "label": cat.name.replace("_", " ").title()}
        for cat in DocumentCategory
    ]
