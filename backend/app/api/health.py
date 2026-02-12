"""
Health check API endpoint.
"""

from fastapi import APIRouter
import logging

from app.models.schemas import HealthResponse
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the API and its dependencies.
    """
    doc_count = 0
    supabase_status = "unknown"
    
    try:
        # Check Supabase/Vector Store
        from app.services.vector_store import VectorStoreService
        vector_store = VectorStoreService()
        doc_count = vector_store.get_document_count()
        supabase_status = "healthy"
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        supabase_status = f"unhealthy: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy" if supabase_status == "healthy" else "degraded",
        version="1.0.0",
        document_count=doc_count,
        chroma_status=supabase_status  # Keeping field name for compatibility
    )


@router.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    settings = get_settings()
    
    return {
        "name": "UniRAG API",
        "version": "1.0.0",
        "description": "RAG Chatbot for University Documents",
        "docs": "/docs",
        "health": "/health",
        "database": "Supabase (pgvector)",
        "configured": bool(settings.supabase_url and settings.openai_api_key)
    }
