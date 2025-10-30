from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # n8n Configuration
    n8n_webhook_url: str
    
    # VAPI Configuration (optional)
    vapi_api_key: str | None = None
    
    # Environment
    environment: str = "production"
    
    # API Configuration
    api_title: str = "Phone Agent API"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
