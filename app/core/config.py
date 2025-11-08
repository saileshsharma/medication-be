from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "Pixel Pirates Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/pixelpirates"
    DATABASE_ECHO: bool = False

    # Redis - Support both REDIS_URL (Railway) and individual settings (local)
    REDIS_URL: Optional[str] = None  # Railway provides this
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 3600

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys
    GOOGLE_FACT_CHECK_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Processing
    MAX_TEXT_LENGTH: int = 10000
    MIN_CONFIDENCE_THRESHOLD: float = 0.6
    ENABLE_CACHING: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # CORS - Allow mobile app in production
    CORS_ORIGINS: str = "*"  # Allow all origins for mobile app (can be comma-separated)
    CORS_ALLOW_CREDENTIALS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
