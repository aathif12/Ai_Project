"""
Chat Service for managing conversations.
Handles conversation state, history, and feedback with Supabase persistence.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from supabase import create_client

from app.config import get_settings, ensure_directories
from app.models import (
    ChatMessage, 
    ChatRequest, 
    ChatResponse, 
    Citation,
    FeedbackRequest
)
from app.services.rag_chain import RAGChain

logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat service for handling conversations.
    
    Features:
    - Conversation history tracking with Supabase
    - Feedback collection
    - Query history persistence
    """
    
    def __init__(self):
        """Initialize the chat service."""
        self.settings = get_settings()
        ensure_directories()
        
        self.rag_chain = RAGChain()
        
        # In-memory cache for active conversations
        self.conversations: Dict[str, List[ChatMessage]] = {}
        
        # Initialize Supabase client
        try:
            self.supabase = create_client(
                self.settings.supabase_url,
                self.settings.supabase_key
            )
            self.use_supabase = True
            logger.info("Chat service using Supabase for persistence")
        except Exception as e:
            logger.warning(f"Supabase not available, using in-memory storage: {e}")
            self.use_supabase = False
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return response.
        
        Args:
            request: ChatRequest with message and optional filters
            
        Returns:
            ChatResponse with answer and citations
        """
        import time
        start_time = time.time()
        
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Load conversation history
        conversation = self._get_conversation(conversation_id)
        
        # Build history for context
        history = self._build_history(conversation)
        
        # Get answer from RAG chain
        answer, citations, confidence = self.rag_chain.answer(
            question=request.message,
            category_filter=request.category_filter,
            conversation_history=history
        )
        
        # Create messages
        user_message = ChatMessage(
            role="user",
            content=request.message,
            citations=None
        )
        
        assistant_message = ChatMessage(
            role="assistant",
            content=answer,
            citations=citations
        )
        
        # Update conversation
        conversation.append(user_message)
        conversation.append(assistant_message)
        self.conversations[conversation_id] = conversation
        
        # Persist to Supabase
        self._save_message(conversation_id, user_message)
        self._save_message(conversation_id, assistant_message)
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=answer,
            citations=citations,
            confidence=confidence,
            processing_time=round(processing_time, 2)
        )
    
    def _get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        """Get or load a conversation."""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Try to load from Supabase
        if self.use_supabase:
            try:
                result = self.supabase.table("chat_history")\
                    .select("*")\
                    .eq("conversation_id", conversation_id)\
                    .order("created_at")\
                    .execute()
                
                messages = []
                for row in result.data:
                    citations = None
                    if row.get("citations"):
                        citations = [
                            Citation(**c) for c in row["citations"]
                        ]
                    messages.append(ChatMessage(
                        role=row["role"],
                        content=row["content"],
                        citations=citations,
                        timestamp=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                    ))
                
                self.conversations[conversation_id] = messages
                return messages
                
            except Exception as e:
                logger.error(f"Error loading conversation from Supabase: {e}")
        
        return []
    
    def _save_message(self, conversation_id: str, message: ChatMessage):
        """Save a message to Supabase."""
        if not self.use_supabase:
            return
        
        try:
            data = {
                "conversation_id": conversation_id,
                "role": message.role,
                "content": message.content,
                "citations": [c.model_dump() for c in message.citations] if message.citations else None,
                "created_at": message.timestamp.isoformat()
            }
            
            self.supabase.table("chat_history").insert(data).execute()
            
        except Exception as e:
            logger.error(f"Error saving message to Supabase: {e}")
    
    def _build_history(
        self, 
        conversation: List[ChatMessage]
    ) -> List[Dict[str, str]]:
        """Build history format for RAG chain."""
        history = []
        for msg in conversation[-10:]:  # Last 5 exchanges
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        return history
    
    def get_conversation_history(
        self, 
        conversation_id: str
    ) -> List[ChatMessage]:
        """Get all messages in a conversation."""
        return self._get_conversation(conversation_id)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations with preview."""
        conversations = []
        
        if self.use_supabase:
            try:
                # Get unique conversation IDs with their latest message
                result = self.supabase.rpc(
                    "get_conversation_previews"
                ).execute()
                
                # If RPC doesn't exist, fall back to regular query
                if not result.data:
                    result = self.supabase.table("chat_history")\
                        .select("conversation_id, content, created_at")\
                        .eq("role", "user")\
                        .order("created_at", desc=True)\
                        .execute()
                    
                    seen = set()
                    for row in result.data:
                        conv_id = row["conversation_id"]
                        if conv_id not in seen:
                            seen.add(conv_id)
                            conversations.append({
                                "id": conv_id,
                                "preview": row["content"][:100] + "..." if len(row["content"]) > 100 else row["content"],
                                "message_count": 0,  # Would need another query
                                "updated_at": row["created_at"]
                            })
                
            except Exception as e:
                logger.error(f"Error listing conversations: {e}")
        
        # Add in-memory conversations
        for conv_id, messages in self.conversations.items():
            if messages and not any(c["id"] == conv_id for c in conversations):
                first_msg = messages[0].content
                conversations.append({
                    "id": conv_id,
                    "preview": first_msg[:100] + "..." if len(first_msg) > 100 else first_msg,
                    "message_count": len(messages),
                    "updated_at": messages[-1].timestamp.isoformat()
                })
        
        # Sort by updated_at descending
        conversations.sort(
            key=lambda x: x.get("updated_at", ""), 
            reverse=True
        )
        
        return conversations
    
    def submit_feedback(self, request: FeedbackRequest) -> bool:
        """
        Submit feedback for a message.
        
        Args:
            request: FeedbackRequest with rating and optional comment
            
        Returns:
            True if feedback was saved
        """
        try:
            if self.use_supabase:
                data = {
                    "conversation_id": request.conversation_id,
                    "message_index": request.message_index,
                    "is_helpful": request.is_helpful,
                    "feedback_text": request.feedback_text,
                }
                self.supabase.table("feedback").insert(data).execute()
            
            logger.info(
                f"Feedback saved: {request.conversation_id}_{request.message_index} - "
                f"{'👍' if request.is_helpful else '👎'}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions for new users."""
        return self.rag_chain.get_suggested_questions()
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation's history."""
        try:
            # Remove from memory
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
            
            # Remove from Supabase
            if self.use_supabase:
                self.supabase.table("chat_history")\
                    .delete()\
                    .eq("conversation_id", conversation_id)\
                    .execute()
            
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False
