"""Celery configuration for background tasks."""
from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.infrastructure.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Requirement 15.3: Retry queue logic is handled in the task itself with @task(bind=True, max_retries=3)
)
