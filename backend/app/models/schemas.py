"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class DocumentCategory(str, Enum):
    """Categories for university documents."""
    RULES = "rules"
    EXAMS = "exams"
    COURSES = "courses"
    HOSTEL = "hostel"
    TIMETABLE = "timetable"
    NOTICES = "notices"
    HANDBOOK = "handbook"
    OTHER = "other"


class UserRole(str, Enum):
    """User roles for access control."""
    ADMIN = "admin"
    STUDENT = "student"


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    id: str
    filename: str
    category: DocumentCategory
    page_count: int
    chunk_count: int
    status: str
    message: str
    uploaded_at: datetime = Field(default_factory=datetime.now)


class DocumentInfo(BaseModel):
    """Information about a stored document."""
    id: str
    filename: str
    category: DocumentCategory
    page_count: int
    chunk_count: int
    file_size: int  # bytes
    uploaded_at: datetime
    uploaded_by: Optional[str] = None


class Citation(BaseModel):
    """Citation/source for an answer."""
    document_name: str
    page_number: Optional[int] = None
    chunk_text: str
    relevance_score: float


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    citations: Optional[List[Citation]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    message: str
    conversation_id: Optional[str] = None
    category_filter: Optional[List[DocumentCategory]] = None


class ChatResponse(BaseModel):
    """Response from the chatbot."""
    conversation_id: str
    message: str
    citations: List[Citation]
    confidence: float  # 0-1 score
    processing_time: float  # seconds


class FeedbackRequest(BaseModel):
    """Feedback on a chat response."""
    conversation_id: str
    message_index: int
    is_helpful: bool
    feedback_text: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    document_count: int
    chroma_status: str
