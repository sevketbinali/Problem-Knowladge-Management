import uuid
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.core.config import settings
from src.infrastructure.services.embedding_service import EmbeddingService

class RAGEngine:
    """Engine for RAG operations using Qdrant and EmbeddingService."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.collection_name = settings.QDRANT_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the Qdrant collection exists with correct vector size."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )

    async def upsert_record(self, record_id: uuid.UUID, text_content: str, metadata: Dict[str, Any]):
        """Requirement 6.2, 11.2: Generate embedding and upsert to Qdrant."""
        vector = await self.embedding_service.generate_embedding(text_content)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(record_id),
                    vector=vector,
                    payload=metadata
                )
            ]
        )

    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Requirement 8.1, 8.2: Search for similar problem records."""
        query_vector = await self.embedding_service.generate_embedding(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False
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
        """Requirement 9.4: Delete record from vector store."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=[str(record_id)]
            )
        )
