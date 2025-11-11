"""
Data Models for Phone Agent API v2.0
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    """Call status enum"""
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"


class CallSentiment(str, Enum):
    """Call sentiment enum"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CallUrgency(str, Enum):
    """Call urgency enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str = Field(..., description="speaker role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CallData(BaseModel):
    """Complete call data"""
    
    # Call Identification
    call_id: str = Field(..., description="Unique call identifier")
    session_id: str = Field(..., description="ElevenLabs session ID")
    
    # Call Metadata
    status: CallStatus = Field(default=CallStatus.INITIATED)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Caller Information
    caller_phone: str = Field(..., description="Caller phone number")
    caller_name: Optional[str] = None
    caller_email: Optional[str] = None
    company_name: Optional[str] = None
    
    # Conversation
    conversation: List[ConversationMessage] = Field(default_factory=list)
    transcript: Optional[str] = None
    summary: Optional[str] = None
    
    # Business Data (extracted by AI)
    call_purpose: Optional[str] = None
    call_urgency: CallUrgency = Field(default=CallUrgency.MEDIUM)
    call_sentiment: CallSentiment = Field(default=CallSentiment.NEUTRAL)
    
    # Actions
    should_book_meeting: bool = False
    meeting_booked: bool = False
    meeting_url: Optional[str] = None
    preferred_time: Optional[str] = None
    
    # CRM Integration
    hubspot_contact_id: Optional[str] = None
    hubspot_company_id: Optional[str] = None
    sheet_row: Optional[int] = None
    
    # Metadata
    language: str = "de-CH"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CompanyKnowledge(BaseModel):
    """Company knowledge base entry"""
    
    id: Optional[str] = None
    title: str = Field(..., description="Knowledge entry title")
    content: str = Field(..., description="Knowledge content")
    category: str = Field(default="general", description="Category: products, services, pricing, faq, etc.")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeSearchResult(BaseModel):
    """Search result from knowledge base"""
    
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    timestamp: str
    version: str
    services: Dict[str, bool]


class CallResponse(BaseModel):
    """API response for call operations"""
    
    status: str
    message: str
    call_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
