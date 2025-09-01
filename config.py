from typing import List, Set, Optional
from functools import lru_cache
import os

class Settings:
    # API
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost,http://localhost:3000,http://localhost:5000"
    ).split(",")
    
    # File Uploads
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "104857600"))  # 100MB
    ALLOWED_EXTENSIONS: Set[str] = set(
        os.getenv("ALLOWED_EXTENSIONS", "mp4,avi,mov,mkv").split(",")
    )
    
    VIDEO_CACHE_TTL: int = int(os.getenv("VIDEO_CACHE_TTL", "86400"))  # 24 hours
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
