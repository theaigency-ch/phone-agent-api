from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VAPICallData(BaseModel):
    """VAPI Call Data Model"""
    
    # Call Information
    call_id: str = Field(..., description="Unique call identifier")
    call_duration: int = Field(..., description="Call duration in seconds")
    call_started_at: str = Field(..., description="Call start timestamp")
    call_ended_at: str = Field(..., description="Call end timestamp")
    
    # Caller Information
    caller_phone: str = Field(..., description="Caller phone number")
    caller_name: Optional[str] = Field(None, description="Caller name (if provided)")
    
    # Call Content
    call_transcript: str = Field(..., description="Full call transcript")
    call_summary: Optional[str] = Field(None, description="AI-generated call summary")
    
    # Business Data (extracted by VAPI AI)
    company_name: Optional[str] = Field(None, description="Company name mentioned")
    call_purpose: Optional[str] = Field(None, description="Purpose of the call")
    call_urgency: Optional[str] = Field("medium", description="Urgency level: low, medium, high")
    
    # Actions
    should_book_meeting: bool = Field(False, description="Should a meeting be booked?")
    should_transfer: bool = Field(False, description="Should call be transferred?")
    preferred_time: Optional[str] = Field(None, description="Preferred meeting time")
    
    # Sentiment Analysis
    call_sentiment: Optional[str] = Field("neutral", description="Call sentiment: positive, neutral, negative")
    
    # Metadata
    vapi_assistant_id: Optional[str] = Field(None, description="VAPI assistant ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "call_id": "call_abc123",
                "call_duration": 180,
                "call_started_at": "2025-10-30T10:00:00Z",
                "call_ended_at": "2025-10-30T10:03:00Z",
                "caller_phone": "+41791234567",
                "caller_name": "Max Muster",
                "call_transcript": "Grüezi, ich möchte gerne einen Termin vereinbaren...",
                "call_summary": "Kunde möchte Demo-Termin für nächste Woche",
                "company_name": "TechStartup AG",
                "call_purpose": "Demo-Termin vereinbaren",
                "call_urgency": "high",
                "should_book_meeting": True,
                "should_transfer": False,
                "preferred_time": "Montag 10-12 Uhr",
                "call_sentiment": "positive",
                "vapi_assistant_id": "asst_123"
            }
        }


class N8NResponse(BaseModel):
    """n8n Webhook Response"""
    
    status: str
    message: str
    lead_id: Optional[str] = None
    meeting_booked: Optional[bool] = None
    meeting_url: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    timestamp: str
    version: str
    n8n_configured: bool
