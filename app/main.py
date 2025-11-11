"""
Phone Agent API v2.0
ElevenLabs + Qdrant + Redis + Direct CRM Integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.config import get_settings
from app.models import HealthResponse
from app.services.elevenlabs_service import ElevenLabsService
from app.services.openai_service import OpenAIService
from app.services.qdrant_service import QdrantService
from app.services.redis_service import RedisService
from app.services.hubspot_service import HubSpotService
from app.services.sheets_service import GoogleSheetsService
from app.services.call_handler import CallHandler
from app.routes import calls

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
    description="Phone Agent API - ElevenLabs Conversational AI with Qdrant Knowledge Base"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calls.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Phone Agent API",
        "version": settings.api_version,
        "status": "running",
        "powered_by": "ElevenLabs + Qdrant + Redis"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    
    services = {
        "elevenlabs": bool(settings.elevenlabs_api_key),
        "openai": bool(settings.openai_api_key),
        "qdrant": False,
        "redis": False,
        "hubspot": bool(settings.hubspot_api_key),
        "google_sheets": bool(settings.google_sheet_id)
    }
    
    # Check Redis
    try:
        redis_service = RedisService()
        services["redis"] = await redis_service.health_check()
    except:
        pass
    
    # Check Qdrant
    try:
        qdrant_service = QdrantService()
        services["qdrant"] = True
    except:
        pass
    
    overall_status = "healthy" if all([
        services["elevenlabs"],
        services["openai"],
        services["qdrant"],
        services["redis"]
    ]) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=settings.api_version,
        services=services
    )


@app.on_event("startup")
async def startup_event():
    """Startup event - Initialize all services"""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize services
    elevenlabs_service = ElevenLabsService()
    logger.info("✅ ElevenLabs service initialized")
    
    openai_service = OpenAIService()
    logger.info("✅ OpenAI service initialized")
    
    qdrant_service = QdrantService()
    logger.info("✅ Qdrant service initialized")
    
    redis_service = RedisService()
    logger.info("✅ Redis service initialized")
    
    # Optional services
    hubspot_service = None
    if settings.hubspot_api_key:
        hubspot_service = HubSpotService()
        logger.info("✅ HubSpot service initialized")
    else:
        logger.warning("⚠️ HubSpot not configured")
    
    sheets_service = None
    if settings.google_sheet_id and settings.google_service_account_file:
        sheets_service = GoogleSheetsService()
        await sheets_service.create_sheet_if_not_exists()
        logger.info("✅ Google Sheets service initialized")
    else:
        logger.warning("⚠️ Google Sheets not configured")
    
    # Initialize call handler
    call_handler = CallHandler(
        elevenlabs_service=elevenlabs_service,
        openai_service=openai_service,
        qdrant_service=qdrant_service,
        redis_service=redis_service,
        hubspot_service=hubspot_service,
        sheets_service=sheets_service
    )
    
    # Inject into routes
    calls.set_services(call_handler, qdrant_service)
    logger.info("✅ Call routes configured")
    
    logger.info("🚀 All services initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info(f"Shutting down {settings.api_title}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
