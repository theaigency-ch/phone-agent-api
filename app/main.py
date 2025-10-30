from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.config import get_settings
from app.models import VAPICallData, N8NResponse, HealthResponse
from app.n8n_client import N8NClient

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()

# FastAPI App
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Phone Agent API - VAPI to n8n Integration"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# n8n Client
n8n_client = N8NClient(webhook_url=settings.n8n_webhook_url)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Phone Agent API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    
    n8n_healthy = await n8n_client.health_check()
    
    return HealthResponse(
        status="healthy" if n8n_healthy else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.api_version,
        n8n_configured=bool(settings.n8n_webhook_url)
    )


@app.post("/vapi/call-ended", response_model=N8NResponse, tags=["VAPI"])
async def handle_vapi_call(call_data: VAPICallData):
    """
    Handle VAPI call-ended webhook
    
    This endpoint receives call data from VAPI after a call ends
    and forwards it to n8n for processing (CRM update, meeting booking, etc.)
    
    Args:
        call_data: VAPI call data
        
    Returns:
        n8n response with processing status
        
    Raises:
        HTTPException: If n8n webhook fails
    """
    try:
        logger.info(f"Received VAPI call: {call_data.call_id}")
        logger.info(f"Caller: {call_data.caller_name or call_data.caller_phone}")
        logger.info(f"Purpose: {call_data.call_purpose}")
        logger.info(f"Should book meeting: {call_data.should_book_meeting}")
        
        # Send to n8n
        n8n_response = await n8n_client.send_call_data(call_data.model_dump())
        
        logger.info(f"n8n processed call: {call_data.call_id}")
        
        return N8NResponse(
            status="success",
            message="Call data processed successfully",
            lead_id=n8n_response.get("lead_id"),
            meeting_booked=n8n_response.get("meeting_booked"),
            meeting_url=n8n_response.get("meeting_url")
        )
        
    except Exception as e:
        logger.error(f"Error processing VAPI call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process call: {str(e)}"
        )


@app.post("/vapi/function-call", tags=["VAPI"])
async def handle_vapi_function_call(function_data: dict):
    """
    Handle VAPI function calls during conversation
    
    This endpoint can be called by VAPI during a conversation
    to check calendar availability, etc.
    
    Args:
        function_data: Function call data from VAPI
        
    Returns:
        Function result
    """
    try:
        function_name = function_data.get("function_name")
        logger.info(f"VAPI function call: {function_name}")
        
        # Here you can implement real-time functions
        # e.g., check_calendar_availability, get_lead_info, etc.
        
        return {
            "status": "success",
            "result": "Function executed"
        }
        
    except Exception as e:
        logger.error(f"Error in function call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
