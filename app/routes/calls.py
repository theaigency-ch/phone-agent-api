"""
Call Routes
API endpoints for phone call management
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.models import CallData, CallResponse, CompanyKnowledge
from app.services.call_handler import CallHandler
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/calls", tags=["Calls"])

# Global service instances (set in main.py)
call_handler: Optional[CallHandler] = None
qdrant_service: Optional[QdrantService] = None


def set_services(handler: CallHandler, qdrant: QdrantService):
    """Set service instances"""
    global call_handler, qdrant_service
    call_handler = handler
    qdrant_service = qdrant


@router.post("/start", response_model=CallResponse)
async def start_call(caller_phone: str):
    """
    Start new phone call
    
    Args:
        caller_phone: Caller phone number
    
    Returns:
        Call data with session ID
    """
    if not call_handler:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Call handler not initialized"
        )
    
    try:
        call_data = await call_handler.start_call(caller_phone)
        
        return CallResponse(
            status="success",
            message="Call started",
            call_id=call_data.call_id,
            data=call_data.model_dump()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting call: {str(e)}"
        )


@router.post("/{call_id}/message", response_model=CallResponse)
async def process_message(call_id: str, message: str):
    """
    Process user message during call
    
    Args:
        call_id: Call identifier
        message: User's message
    
    Returns:
        AI response
    """
    if not call_handler:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Call handler not initialized"
        )
    
    try:
        ai_response = await call_handler.process_user_message(call_id, message)
        
        return CallResponse(
            status="success",
            message="Message processed",
            call_id=call_id,
            data={"ai_response": ai_response}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/{call_id}/end", response_model=CallResponse)
async def end_call(call_id: str):
    """
    End phone call and process final data
    
    Args:
        call_id: Call identifier
    
    Returns:
        Final call data
    """
    if not call_handler:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Call handler not initialized"
        )
    
    try:
        call_data = await call_handler.end_call(call_id)
        
        return CallResponse(
            status="success",
            message="Call ended",
            call_id=call_id,
            data=call_data.model_dump()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending call: {str(e)}"
        )


@router.post("/knowledge", response_model=CallResponse)
async def add_knowledge(knowledge: CompanyKnowledge):
    """
    Add company knowledge to database
    
    Args:
        knowledge: Knowledge entry
    
    Returns:
        Entry ID
    """
    if not qdrant_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service not initialized"
        )
    
    try:
        entry_id = await qdrant_service.add_knowledge(knowledge)
        
        return CallResponse(
            status="success",
            message="Knowledge added",
            data={"entry_id": entry_id}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding knowledge: {str(e)}"
        )


@router.get("/knowledge", response_model=CallResponse)
async def get_knowledge(category: Optional[str] = None):
    """Get all knowledge entries"""
    if not qdrant_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service not initialized"
        )
    
    try:
        entries = await qdrant_service.get_all_knowledge(category)
        
        return CallResponse(
            status="success",
            message=f"Found {len(entries)} entries",
            data={"entries": [e.model_dump() for e in entries]}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting knowledge: {str(e)}"
        )


@router.delete("/knowledge/{entry_id}", response_model=CallResponse)
async def delete_knowledge(entry_id: str):
    """Delete knowledge entry"""
    if not qdrant_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service not initialized"
        )
    
    try:
        success = await qdrant_service.delete_knowledge(entry_id)
        
        if success:
            return CallResponse(
                status="success",
                message="Knowledge deleted"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting knowledge: {str(e)}"
        )
