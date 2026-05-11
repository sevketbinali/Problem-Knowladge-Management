"""RAG engine for semantic search and retrieval of problem records."""
import uuid
from typing import Any, Dict, List, Optional

from src.infrastructure.repositories.qdrant_repository import QdrantRepository
from src.infrastructure.services.embedding_service import EmbeddingService


class RAGEngine:
    def __init__(self, embedding_service: EmbeddingService, qdrant_repo: QdrantRepository):
        self.embedding_service = embedding_service
        self.qdrant_repo = qdrant_repo

    async def index_record(self, record_id: uuid.UUID, text: str, metadata: Dict[str, Any]):
        """Generate embedding and index a record."""
        vector = await self.embedding_service.generate_embedding(text)
        # Store metadata in payload
        payload = {
            "text": text,
            "metadata": metadata
        }
        await self.qdrant_repo.index_record(record_id, vector, payload)

    async def search_similar(self, query: str, limit: int = 10, score_threshold: float = 0.5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for records similar to the query."""
        # Requirement 8.1, 16.1: Semantic search
        vector = await self.embedding_service.generate_embedding(query)
        results = await self.qdrant_repo.search_similar(
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters
        )
        
        # Requirement 8.2: Results in descending order of similarity
        # Qdrant already returns results sorted by score descending.
        return results

    async def delete_record(self, record_id: uuid.UUID):
        """Delete a record from index."""
        await self.qdrant_repo.delete_record(record_id)

    async def update_record(self, record_id: uuid.UUID, text: str, metadata: Dict[str, Any]):
        """Update a record in index."""
        await self.index_record(record_id, text, metadata)
