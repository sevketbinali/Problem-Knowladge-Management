"""Application configuration from environment variables."""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_COLLECTION: str = "problem_records"
    QDRANT_API_KEY: Optional[str] = None
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600  # 60 minutes
    RATE_LIMIT_PER_MINUTE: int = 10
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 3072
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    INITIAL_ADMIN_EMAIL: str = "admin@pkm.local"
    INITIAL_ADMIN_PASSWORD: str = "Admin123!"

    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.QDRANT_URL = os.getenv("QDRANT_URL", "")
        self.QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "problem_records")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.REDIS_URL = os.getenv("REDIS_URL", "")
        self.REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "3600"))
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        self.JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret_for_dev_only")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.INITIAL_ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "admin@pkm.local")
        self.INITIAL_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin123!")


settings = Settings()

