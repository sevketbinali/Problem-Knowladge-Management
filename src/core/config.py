"""Application configuration from environment variables."""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    QDRANT_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str
    JWT_SECRET: str

    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.QDRANT_URL = os.getenv("QDRANT_URL", "")
        self.REDIS_URL = os.getenv("REDIS_URL", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.JWT_SECRET = os.getenv("JWT_SECRET", "")


settings = Settings()
