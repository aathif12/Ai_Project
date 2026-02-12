"""
Chat API endpoints for the RAG chatbot.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from app.models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    FeedbackRequest
)
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the chatbot.
    
    The message will be processed through the RAG pipeline:
    1. Embedded and matched against document vectors
    2. Relevant chunks retrieved
    3. LLM generates grounded response
    4. Response returned with citations
    """
    try:
        chat_service = ChatService()
        response = chat_service.chat(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation_history(conversation_id: str):
    """
    Get the message history for a conversation.
    """
    try:
        chat_service = ChatService()
        history = chat_service.get_conversation_history(conversation_id)
        return history
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations() -> List[Dict[str, Any]]:
    """
    List all conversations with preview.
    """
    try:
        chat_service = ChatService()
        conversations = chat_service.list_conversations()
        return conversations
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    """
    try:
        chat_service = ChatService()
        success = chat_service.clear_conversation(conversation_id)
        
        if success:
            return {"status": "success", "message": "Conversation deleted"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chat response.
    
    Use this to rate responses as helpful or not helpful,
    which helps improve the system.
    """
    try:
        chat_service = ChatService()
        success = chat_service.submit_feedback(request)
        
        if success:
            return {"status": "success", "message": "Feedback submitted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions() -> List[str]:
    """
    Get suggested questions for new users.
    
    Returns questions based on available documents.
    """
    try:
        chat_service = ChatService()
        suggestions = chat_service.get_suggested_questions()
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
