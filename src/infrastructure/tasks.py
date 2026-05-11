"""Celery background tasks."""
import asyncio
import uuid
from typing import Any, Dict

from src.infrastructure.celery_app import celery_app
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.repositories.qdrant_repository import QdrantRepository


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_embedding_task(self, record_id: str, text: str, metadata: Dict[str, Any]):
    """Background task to generate embedding and index into Qdrant."""
    async def _run():
        embedding_service = EmbeddingService()
        qdrant_repo = QdrantRepository()
        
        try:
            # Ensure collection exists before indexing
            await qdrant_repo.ensure_collection()
            
            # Generate embedding
            vector = await embedding_service.generate_embedding(text)
            
            # Index into Qdrant
            payload = {
                "text": text,
                "metadata": metadata
            }
            await qdrant_repo.index_record(uuid.UUID(record_id), vector, payload)
            
        except Exception as exc:
            # Requirement 15.3: Retry mechanism
            print(f"Embedding Task Error: {str(exc)}")
            raise self.retry(exc=exc)

    # Run the async loop
    asyncio.run(_run())
