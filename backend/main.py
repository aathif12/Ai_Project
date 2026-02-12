"""
UniRAG - University Document RAG Chatbot
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings, ensure_directories
from app.api import documents_router, chat_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="UniRAG API",
    description="""
    # 🎓 UniRAG - University Document Chatbot
    
    A RAG (Retrieval-Augmented Generation) chatbot that answers questions 
    based on university documents like handbooks, rules, timetables, and notices.
    
    ## Features
    
    - 📄 **Document Upload**: Upload PDF and DOCX files
    - 💬 **Chat Interface**: Ask questions in natural language
    - 🎯 **Grounded Answers**: Responses based only on uploaded documents
    - 📍 **Citations**: Every answer includes source references
    - 🚫 **Hallucination Guard**: System refuses to make up information
    
    ## How it works
    
    1. Upload your university documents (PDF/DOCX)
    2. Documents are processed and stored in a vector database
    3. Ask questions through the chat endpoint
    4. Get accurate answers with citations to source documents
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Starting UniRAG API...")
    
    # Ensure directories exist
    ensure_directories()
    
    settings = get_settings()
    logger.info(f"📁 Upload directory: {settings.upload_dir}")
    logger.info(f"🗄️ ChromaDB directory: {settings.chroma_persist_dir}")
    logger.info(f"🤖 LLM Model: {settings.llm_model}")
    logger.info(f"📊 Embedding Model: {settings.embedding_model}")
    
    logger.info("✅ UniRAG API started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 Shutting down UniRAG API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
