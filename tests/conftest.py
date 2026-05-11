import os
import pytest

# Set dummy environment variables for testing
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/test_db"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["JWT_SECRET"] = "test_secret"

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/test_db")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("JWT_SECRET", "test_secret")
