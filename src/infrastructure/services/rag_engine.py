import uuid
import time
from typing import List, Dict, Any, Optional

from src.infrastructure.repositories.qdrant_repository import QdrantRepository
from src.infrastructure.services.embedding_service import EmbeddingService

class RAGEngine:
    """Engine for RAG operations using QdrantRepository and EmbeddingService."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.repository = QdrantRepository()
        self._degraded_mode = False
        self._last_error_time = 0
        self._error_count = 0
        self._recovery_timeout = 60 # Recovery after 60 seconds

    def _check_degraded(self):
        """Check if we are in degraded mode and if we should try to recover."""
        if self._degraded_mode:
            if time.time() - self._last_error_time > self._recovery_timeout:
                self._degraded_mode = False
                self._error_count = 0
        return self._degraded_mode

    def _record_error(self):
        """Record an error and potentially enter degraded mode."""
        self._error_count += 1
        self._last_error_time = time.time()
        if self._error_count >= 3:
            self._degraded_mode = True

    async def upsert_record(self, record_id: uuid.UUID, text_content: str, metadata: Dict[str, Any]):
        """Requirement 6.2: Generate embedding and upsert to Qdrant."""
        try:
            vector = await self.embedding_service.generate_embedding(text_content)
            await self.repository.index_record(record_id, vector, metadata)
            self._error_count = 0 # Reset on success
        except Exception:
            self._record_error()
            raise

    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Requirement 8.1, 8.2: Search for similar problem records with degraded mode support."""
        if self._check_degraded():
            # Requirement 23.1: Return empty results or raise specific error in degraded mode
            # For sessions, we want to continue, so we return empty list
            return []

        try:
            query_vector = await self.embedding_service.generate_embedding(query)
            results = await self.repository.search_similar(query_vector, limit=limit)
            self._error_count = 0
            return results
        except Exception:
            self._record_error()
            # If it's a search, we might want to return empty to allow session to continue (Task 23.2)
            return []

    async def delete_record(self, record_id: uuid.UUID):
        """Requirement 9.4: Delete record from vector store."""
        try:
            await self.repository.delete_record(record_id)
            self._error_count = 0
        except Exception:
            self._record_error()
            raise
