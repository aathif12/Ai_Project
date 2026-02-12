"""
Complete ingestion pipeline for document processing.
Orchestrates extraction, chunking, embedding, and storing.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from app.config import get_settings, ensure_directories
from app.models import DocumentCategory, DocumentUploadResponse
from app.ingestion.extractor import DocumentExtractor
from app.ingestion.chunker import TextChunker
from app.ingestion.embedder import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete document ingestion pipeline.
    
    Pipeline steps:
    1. Extract text from PDF/DOCX
    2. Split text into chunks
    3. Generate embeddings
    4. Store in vector database
    """
    
    def __init__(self):
        """Initialize the pipeline with all required services."""
        self.settings = get_settings()
        ensure_directories()
        
        self.chunker = TextChunker(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()
    
    def ingest_document(
        self,
        file_path: str,
        filename: str,
        category: DocumentCategory,
        uploaded_by: Optional[str] = None
    ) -> DocumentUploadResponse:
        """
        Process and store a document.
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            category: Document category
            uploaded_by: Optional uploader identifier
            
        Returns:
            DocumentUploadResponse with processing results
        """
        document_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting ingestion for: {filename} (ID: {document_id})")
            
            # Step 1: Extract text from document
            logger.info("Step 1: Extracting text...")
            pages = DocumentExtractor.extract(file_path)
            page_count = len(pages)
            
            if not pages:
                return DocumentUploadResponse(
                    id=document_id,
                    filename=filename,
                    category=category,
                    page_count=0,
                    chunk_count=0,
                    status="error",
                    message="No text content found in document"
                )
            
            # Step 2: Chunk the text
            logger.info("Step 2: Chunking text...")
            chunks = self.chunker.chunk_pages(
                pages=pages,
                document_name=filename,
                category=category.value
            )
            
            if not chunks:
                return DocumentUploadResponse(
                    id=document_id,
                    filename=filename,
                    category=category,
                    page_count=page_count,
                    chunk_count=0,
                    status="error",
                    message="No chunks created from document"
                )
            
            # Step 3: Generate embeddings
            logger.info(f"Step 3: Generating embeddings for {len(chunks)} chunks...")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.embedder.get_embeddings(chunk_texts)
            
            # Step 4: Store in vector database
            logger.info("Step 4: Storing in vector database...")
            self._store_chunks(
                document_id=document_id,
                filename=filename,
                category=category,
                chunks=chunks,
                embeddings=embeddings,
                uploaded_by=uploaded_by
            )
            
            logger.info(
                f"Successfully ingested {filename}: "
                f"{page_count} pages, {len(chunks)} chunks"
            )
            
            return DocumentUploadResponse(
                id=document_id,
                filename=filename,
                category=category,
                page_count=page_count,
                chunk_count=len(chunks),
                status="success",
                message=f"Document processed successfully. Created {len(chunks)} searchable chunks."
            )
            
        except Exception as e:
            logger.error(f"Error ingesting document {filename}: {e}")
            return DocumentUploadResponse(
                id=document_id,
                filename=filename,
                category=category,
                page_count=0,
                chunk_count=0,
                status="error",
                message=f"Error processing document: {str(e)}"
            )
    
    def _store_chunks(
        self,
        document_id: str,
        filename: str,
        category: DocumentCategory,
        chunks: list,
        embeddings: list,
        uploaded_by: Optional[str]
    ):
        """Store chunks with embeddings in vector database."""
        
        ids = []
        documents = []
        metadatas = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{document_id}_{i}"
            
            ids.append(chunk_id)
            documents.append(chunk.text)
            metadatas.append({
                "document_id": document_id,
                "document_name": filename,
                "category": category.value,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "uploaded_by": uploaded_by or "unknown",
                "uploaded_at": datetime.now().isoformat(),
            })
        
        self.vector_store.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks from the vector store.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful
        """
        try:
            self.vector_store.delete_by_document_id(document_id)
            logger.info(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
