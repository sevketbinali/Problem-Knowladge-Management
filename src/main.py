"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.core.config import settings
from src.infrastructure.repositories.qdrant_repository import QdrantRepository
from src.infrastructure.services.redis_service import RedisService



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Problem Knowledge Management System",
    description="AI-destekli Problem Bilgi Yönetim Sistemi",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
from src.api.v1.analysis import router as analysis_router
from src.api.v1.auth import router as auth_router
from src.api.v1.search import router as search_router
from src.api.v1.sessions import router as session_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(session_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")



@app.get("/health")
async def health():
    """Health check endpoint — returns 200 if the API process is running."""
    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": {"healthy": True}, "error": None},
    )


@app.get("/ready")
async def ready(
    db_session: AsyncSession = Depends(get_db)
):
    """Readiness check endpoint — returns 200 when all dependencies are reachable."""
    # Check PostgreSQL
    try:
        await db_session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Database unreachable"})

    # Check Qdrant
    qdrant = QdrantRepository()
    if not await qdrant.is_healthy():
         return JSONResponse(status_code=503, content={"status": "error", "message": "Qdrant unreachable"})

    # Check Redis
    redis = RedisService()
    try:
        await redis.client.ping()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Redis unreachable"})
    finally:
        await redis.close()

    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": {"ready": True}, "error": None},
    )

