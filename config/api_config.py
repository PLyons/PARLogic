from pydantic_settings import BaseSettings
from typing import List
import os

class APISettings(BaseSettings):
    """API Configuration Settings"""
    
    # API Settings
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "PARLogic API"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".csv"]
    UPLOAD_DIR: str = "data/uploads"
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = APISettings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 