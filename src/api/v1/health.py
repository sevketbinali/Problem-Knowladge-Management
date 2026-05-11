"""Health router for liveness and readiness checks."""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.api.v1.schemas import APIResponse
from src.infrastructure.repositories.qdrant_repository import QdrantRepository
from src.infrastructure.services.redis_service import RedisService

router = APIRouter(prefix="/health", tags=["System Health"])


@router.get("", response_model=APIResponse[dict])
async def health_check():
    """Liveness check: returns 200 if the API process is running."""
    return APIResponse(data={"healthy": True})


@router.get("/ready", response_model=APIResponse[dict])
async def readiness_check(
    db_session: AsyncSession = Depends(get_db)
):
    """Readiness check: returns 200 when all dependencies are reachable."""
    # Check PostgreSQL
    try:
        await db_session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "data": None,
                "error": "Database unreachable",
                "message": None
            }
        )

    # Check Qdrant
    qdrant = QdrantRepository()
    if not await qdrant.is_healthy():
         return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "data": None,
                "error": "Qdrant unreachable",
                "message": None
            }
        )

    # Check Redis
    redis = RedisService()
    try:
        await redis.client.ping()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "data": None,
                "error": "Redis unreachable",
                "message": None
            }
        )
    finally:
        await redis.close()

    return APIResponse(data={"ready": True})
