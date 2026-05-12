"""Service for searching problem records with semantic and metadata filters."""
import uuid
from typing import Any, Dict, List, Optional

from src.infrastructure.services.rag_engine import RAGEngine
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.redis_service import RedisService


class SearchService:
    def __init__(
        self, 
        rag_engine: RAGEngine, 
        redis_service: RedisService,
        repository: PostgreSQLRepository
    ):
        self.rag = rag_engine
        self.redis = redis_service
        self.repository = repository

    async def search(
        self, 
        user_id: uuid.UUID,
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for records using semantic similarity and optional filters.
        Requirement 21.2: Redis caching
        Requirement 21.3: Audit logging
        Requirement 23.1: Degraded mode
        """
        # Requirement 23.1: Check health
        if not await self.rag.repository.is_healthy():
            raise RuntimeError("Search is currently unavailable (Degraded Mode)")

        # Create cache key

        filter_str = str(sorted(filters.items())) if filters else ""
        cache_key = f"search:{query}:{filter_str}:{limit}"
        
        # Check cache
        cached_results = await self.redis.get_cache(cache_key)
        if cached_results:
            # Audit log even for cache hits
            await self.repository.create_audit_log(
                user_id=user_id,
                operation="search_cache_hit",
                entity_type="problem_record",
                entity_id=uuid.UUID(int=0), # Dummy ID for search
                after_values={"query": query, "results_count": len(cached_results)}
            )
            return cached_results

        # Perform semantic search
        results = await self.rag.search_similar(
            query=query,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
        
        # Save to cache
        await self.redis.set_cache(cache_key, results)
        
        # Requirement 21.3: Audit log
        await self.repository.create_audit_log(
            user_id=user_id,
            operation="search_perform",
            entity_type="problem_record",
            entity_id=uuid.UUID(int=0),
            after_values={"query": query, "results_count": len(results)}
        )
        
        return results
