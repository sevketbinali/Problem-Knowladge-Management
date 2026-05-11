"""Repository for interacting with Qdrant vector database."""
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

from src.core.config import settings


class QdrantRepository:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.QDRANT_COLLECTION

    async def ensure_collection(self):
        """Ensure the collection exists with correct parameters."""
        collections = await self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                ),
                # Requirement 15.2: HNSW parameters
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100
                )
            )

    async def index_record(self, record_id: uuid.UUID, vector: List[float], payload: Dict[str, Any]):
        """Index a problem record into Qdrant."""
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(record_id),
                    vector=vector,
                    payload=payload
                )
            ]
        )

    async def search_similar(self, vector: List[float], limit: int = 10, score_threshold: float = 0.5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar records in Qdrant."""
        # Convert filters to Qdrant format if provided
        query_filter = None
        if filters:
            # Basic implementation of filters, could be expanded
            must = []
            for key, value in filters.items():
                must.append(models.FieldCondition(key=f"metadata.{key}", match=models.MatchValue(value=value)))
            query_filter = models.Filter(must=must)

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]

    async def delete_record(self, record_id: uuid.UUID):
        """Delete a record from Qdrant."""
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=[str(record_id)]
            )
        )

    async def update_record(self, record_id: uuid.UUID, vector: List[float], payload: Dict[str, Any]):
        """Update a record in Qdrant (same as upsert)."""
        await self.index_record(record_id, vector, payload)

    async def is_healthy(self) -> bool:
        """Requirement 23.1: Check if Qdrant is reachable."""
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False

