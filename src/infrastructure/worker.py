import asyncio
import uuid
from typing import Dict, Any

from celery import Celery
from src.core.config import settings
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.services.rag_engine import RAGEngine
from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

celery_app = Celery(
    "pkm_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configuration for retries
celery_app.conf.task_soft_time_limit = 300
celery_app.conf.task_time_limit = 600

@celery_app.task(
    name="process_problem_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=30  # 30 seconds delay between retries
)
def process_problem_embedding(self, record_id_str: str, text_content: str, metadata: Dict[str, Any]):
    """Background task to generate embedding and upsert to vector store."""
    record_id = uuid.UUID(record_id_str)
    
    # We need to run async code inside Celery (which is sync by default)
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    async def _run():
        embedding_service = EmbeddingService()
        rag_engine = RAGEngine(embedding_service)
        
        try:
            await rag_engine.upsert_record(record_id, text_content, metadata)
            
            # Update status in DB to COMPLETED
            async with AsyncSessionLocal() as session:
                repo = PostgreSQLRepository(session)
                await repo.update_record(record_id, embedding_status="completed")
                await session.commit()
                
        except Exception as e:
            # Update status in DB to FAILED (temporarily)
            async with AsyncSessionLocal() as session:
                repo = PostgreSQLRepository(session)
                await repo.update_record(record_id, embedding_status="failed")
                await session.commit()
            
            # Retry the task
            raise self.retry(exc=e)

    try:
        loop.run_until_complete(_run())
    except Exception as e:
        # Final failure after retries will be caught by Celery
        print(f"Final failure for record {record_id}: {str(e)}")
        # In actual production, we might want to log this to a monitoring system
        raise e
