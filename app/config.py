from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Phone Agent API"
    api_version: str = "2.0.0"
    environment: str = "production"
    
    # ElevenLabs Configuration
    elevenlabs_api_key: str
    elevenlabs_agent_id: str | None = None
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # Qdrant Configuration
    qdrant_url: str = "http://qdrant-agents:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "company_knowledge"
    
    # Redis Configuration
    redis_url: str = "redis://redis-agents:6379"
    redis_password: str | None = None
    
    # HubSpot Configuration
    hubspot_api_key: str | None = None
    
    # Google Sheets Configuration
    google_sheets_credentials: str | None = None
    google_service_account_file: str | None = "/app/service-account.json"
    google_sheet_id: str | None = None
    
    # Gmail Configuration
    sender_email: str | None = None
    notification_email: str | None = None
    
    # Twilio WhatsApp (for alerts)
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_whatsapp_from: str | None = None
    twilio_whatsapp_to: str | None = None
    
    # Brand Settings
    brand_name: str = "Your Company"
    company_description: str = "AI-powered business solutions"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Only load .env if it exists, otherwise use system ENV
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
