"""Search router for semantic queries."""
from typing import List
from fastapi import APIRouter, Depends

from src.api.v1.dependencies import (
    check_rate_limit,
    get_current_active_user,
    get_redis,
    get_repository,
)
from src.api.v1.schemas import SearchQuery, SearchResult
from src.domain.rag_engine import RAGEngine
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.repositories.qdrant_repository import QdrantRepository
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.services.redis_service import RedisService
from src.infrastructure.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


def get_search_service(
    repo: PostgreSQLRepository = Depends(get_repository),
    redis: RedisService = Depends(get_redis)
) -> SearchService:
    rag = RAGEngine(QdrantRepository(), EmbeddingService())
    return SearchService(rag, redis, repo)


@router.post("/", response_model=List[SearchResult], dependencies=[Depends(check_rate_limit)])
async def search_records(
    query: SearchQuery,
    current_user: User = Depends(get_current_active_user),
    service: SearchService = Depends(get_search_service)
):
    try:
        return await service.search(
            user_id=current_user.id,
            query=query.query,
            filters=query.filters,
            limit=query.limit
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

