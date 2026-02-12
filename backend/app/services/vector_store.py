"""
Supabase Vector Store Service.
Handles storage and retrieval of document embeddings using Supabase with pgvector.
"""

import vecs
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from app.config import get_settings, ensure_directories

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Vector store service using Supabase pgvector.
    
    Supabase provides:
    - Cloud-hosted PostgreSQL with pgvector extension
    - Scalable vector similarity search
    - Integration with Supabase Auth and Storage
    """
    
    COLLECTION_NAME = "university_documents"
    
    def __init__(self):
        """Initialize Supabase client and vector collection."""
        settings = get_settings()
        ensure_directories()
        
        # Validate required settings
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        if not settings.supabase_db_url:
            raise ValueError(
                "Supabase database URL not configured. "
                "Set SUPABASE_DB_URL environment variable."
            )
        
        # Initialize Supabase client (for table operations)
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        
        # Initialize vecs client for vector operations
        self.vx = vecs.create_client(settings.supabase_db_url)
        
        # Get or create the vector collection
        self.collection = self.vx.get_or_create_collection(
            name=self.COLLECTION_NAME,
            dimension=settings.embedding_dimensions
        )
        
        # Create index for faster similarity search
        try:
            self.collection.create_index()
        except Exception:
            # Index might already exist
            pass
        
        logger.info(
            f"Vector store initialized. Collection '{self.COLLECTION_NAME}' ready."
        )
    
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Add documents with their embeddings to the store.
        
        Args:
            ids: Unique identifiers for each document
            documents: The text content
            embeddings: Pre-computed embedding vectors
            metadatas: Metadata for each document
        """
        try:
            # Prepare records for vecs
            # vecs format: (id, embedding, metadata)
            records = []
            for id_, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
                # Add document text to metadata for retrieval
                meta_with_text = {
                    **meta,
                    "text": doc,
                }
                records.append((id_, emb, meta_with_text))
            
            # Upsert records
            self.collection.upsert(records=records)
            
            logger.info(f"Added {len(ids)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        category_filter: Optional[List[str]] = None,
        document_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents using embedding.
        
        Args:
            query_embedding: The query embedding vector
            n_results: Number of results to return
            category_filter: Optional list of categories to filter by
            document_filter: Optional list of document IDs to filter by
            
        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        try:
            # Build filters for vecs
            filters = {}
            if category_filter:
                filters["category"] = {"$in": category_filter}
            if document_filter:
                filters["document_id"] = {"$in": document_filter}
            
            # Query the collection
            results = self.collection.query(
                data=query_embedding,
                limit=n_results,
                filters=filters if filters else None,
                include_value=True,  # Include distance
                include_metadata=True
            )
            
            # Format results
            ids = []
            documents = []
            metadatas = []
            distances = []
            
            for result in results:
                ids.append(result[0])  # id
                
                # Metadata contains the text
                meta = result[2] if len(result) > 2 else {}
                text = meta.pop("text", "")
                
                documents.append(text)
                metadatas.append(meta)
                distances.append(result[1] if len(result) > 1 else 0)  # distance
            
            return {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
                "distances": distances,
            }
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_document_count(self) -> int:
        """Get total number of documents in the store."""
        try:
            # Get all records (limited) just to count
            # Note: This is not efficient for large collections
            # In production, you might want to query the database directly
            results = self.collection.query(
                data=[0.0] * get_settings().embedding_dimensions,  # dummy embedding
                limit=10000,
                include_value=False,
                include_metadata=False
            )
            return len(results)
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def get_unique_documents(self) -> List[Dict[str, Any]]:
        """Get list of unique uploaded documents with metadata."""
        try:
            # Query with a dummy embedding to get all records
            settings = get_settings()
            results = self.collection.query(
                data=[0.0] * settings.embedding_dimensions,
                limit=10000,
                include_value=False,
                include_metadata=True
            )
            
            # Extract unique documents
            documents = {}
            for result in results:
                meta = result[2] if len(result) > 2 else {}
                doc_id = meta.get("document_id")
                
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "document_name": meta.get("document_name"),
                        "category": meta.get("category"),
                        "uploaded_at": meta.get("uploaded_at"),
                        "uploaded_by": meta.get("uploaded_by"),
                    }
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error getting unique documents: {e}")
            return []
    
    def delete_by_document_id(self, document_id: str):
        """Delete all chunks belonging to a document."""
        try:
            # Get all IDs for this document first
            settings = get_settings()
            results = self.collection.query(
                data=[0.0] * settings.embedding_dimensions,
                limit=10000,
                filters={"document_id": {"$eq": document_id}},
                include_value=False,
                include_metadata=False
            )
            
            # Delete by IDs
            ids_to_delete = [r[0] for r in results]
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(
                    f"Deleted {len(ids_to_delete)} chunks for document {document_id}"
                )
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    def clear_all(self):
        """Clear all documents from the collection. Use with caution!"""
        try:
            # Delete and recreate the collection
            self.vx.delete_collection(self.COLLECTION_NAME)
            
            settings = get_settings()
            self.collection = self.vx.get_or_create_collection(
                name=self.COLLECTION_NAME,
                dimension=settings.embedding_dimensions
            )
            self.collection.create_index()
            
            logger.warning("Cleared all documents from vector store")
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
