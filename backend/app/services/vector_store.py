"""
Supabase Vector Store Service.
Uses Supabase REST API + SQL functions for vector operations.
No direct database connection needed - works purely through the Supabase client.
"""

from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import logging
import json
import uuid
from datetime import datetime

from app.config import get_settings, ensure_directories

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Vector store service using Supabase REST API with pgvector.
    
    Uses Supabase's RPC (Remote Procedure Calls) for vector operations,
    avoiding direct database connections and pooler issues.
    """
    
    TABLE_NAME = "documents"
    
    def __init__(self):
        """Initialize Supabase client."""
        settings = get_settings()
        ensure_directories()
        
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        self.dimensions = settings.embedding_dimensions
        
        logger.info("Vector store initialized with Supabase REST API.")
    
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Add documents with their embeddings to the store.
        """
        try:
            records = []
            for id_, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
                records.append({
                    "id": id_,
                    "content": doc,
                    "embedding": emb,
                    "metadata": meta
                })
            
            # Batch insert using Supabase client
            # Insert in batches of 50 to avoid payload limits
            batch_size = 50
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                self.supabase.table(self.TABLE_NAME).upsert(batch).execute()
            
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
        Search for similar documents using embedding via RPC function.
        """
        try:
            # Call the match_documents RPC function
            params = {
                "query_embedding": query_embedding,
                "match_count": n_results,
            }
            
            # Add optional filters
            if category_filter:
                params["filter_category"] = category_filter[0] if len(category_filter) == 1 else None
            
            result = self.supabase.rpc("match_documents", params).execute()
            
            # Format results
            ids = []
            documents = []
            metadatas = []
            distances = []
            
            for row in result.data:
                ids.append(row.get("id", ""))
                documents.append(row.get("content", ""))
                
                meta = row.get("metadata", {})
                if isinstance(meta, str):
                    meta = json.loads(meta)
                metadatas.append(meta)
                
                # similarity is returned (higher = more similar)
                similarity = row.get("similarity", 0)
                distances.append(1.0 - similarity)  # Convert to distance
            
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
        """Get total number of document chunks in the store."""
        try:
            result = self.supabase.table(self.TABLE_NAME)\
                .select("id", count="exact")\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def get_unique_documents(self) -> List[Dict[str, Any]]:
        """Get list of unique uploaded documents with metadata."""
        try:
            result = self.supabase.table(self.TABLE_NAME)\
                .select("metadata")\
                .execute()
            
            documents = {}
            for row in result.data:
                meta = row.get("metadata", {})
                if isinstance(meta, str):
                    meta = json.loads(meta)
                    
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
            # Use contains filter on metadata JSONB
            self.supabase.table(self.TABLE_NAME)\
                .delete()\
                .filter("metadata->>document_id", "eq", document_id)\
                .execute()
            
            logger.info(f"Deleted chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    def clear_all(self):
        """Clear all documents from the store. Use with caution!"""
        try:
            self.supabase.table(self.TABLE_NAME)\
                .delete()\
                .neq("id", "00000000-0000-0000-0000-000000000000")\
                .execute()
            
            logger.warning("Cleared all documents from vector store")
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
