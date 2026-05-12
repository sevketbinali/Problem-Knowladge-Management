"""Knowledge router for searching and retrieving problem records."""
import uuid
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.dependencies import (
    check_rate_limit,
    get_current_active_user,
    get_redis,
    get_repository,
    get_rag_engine
)
from src.api.v1.schemas import APIResponse, SearchQuery, SearchResult, ProblemRecord
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.rag_engine import RAGEngine
from src.infrastructure.services.redis_service import RedisService
from src.infrastructure.services.search_service import SearchService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


def get_search_service(
    repo: PostgreSQLRepository = Depends(get_repository),
    redis: RedisService = Depends(get_redis),
    rag: RAGEngine = Depends(get_rag_engine)
) -> SearchService:
    return SearchService(rag, redis, repo)


@router.get("/search", response_model=APIResponse[List[SearchResult]], dependencies=[Depends(check_rate_limit)])
async def search_records(
    query: str,
    industry: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    service: SearchService = Depends(get_search_service)
):
    """Requirement 8.1, 8.5: Search records with filters and rate limiting."""
    try:
        filters = {}
        if industry: filters["industry_sector"] = industry
        if department: filters["department"] = department
        
        result = await service.search(
            user_id=current_user.id,
            query=query,
            filters=filters,
            limit=10,
            score_threshold=0.65
        )
        return APIResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get("/records/{record_id}", response_model=APIResponse[ProblemRecord])
async def get_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 8.3, 8.4: Retrieve full problem record."""
    record = await repo.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return APIResponse(data=record)
