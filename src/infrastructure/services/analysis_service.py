"""Service for analyzing completed sessions and generating final reports."""
import uuid
from datetime import datetime
from typing import Any, Dict, List

from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.llm_service import LLMService
from src.infrastructure.tasks import generate_embedding_task


class AnalysisService:
    def __init__(self, repository: PostgreSQLRepository, llm_service: LLMService):
        self.repository = repository
        self.llm = llm_service

    async def generate_final_report(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """Generate final report and lessons learned from a completed session."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
        
        if db_session.status != "completed":
            raise ValueError("Session is not completed yet")

        # Prepare context for LLM
        session_data = {
            "problem_description": db_session.problem_description,
            "methodology": db_session.methodology,
            "responses": db_session.step_responses
        }

        # Requirement 20.2: Lessons Learned via LLM
        lessons_learned = await self.llm.generate_lessons_learned(session_data)
        
        # In a real app, we would ask LLM to also extract root cause and title
        # For now, we simulate or use parts of the responses
        title = f"Analiz: {db_session.problem_description[:50]}..."
        root_cause = "LLM tarafından analiz edilen kök neden." # Simplified
        corrective_actions = ["Aksiyon 1", "Aksiyon 2"] # Simplified

        # Save ProblemRecord to PostgreSQL
        record = await self.repository.create_record(
            session_id=session_id,
            user_id=db_session.user_id,
            title=title,
            problem_description=db_session.problem_description,
            methodology=db_session.methodology,
            step_responses=db_session.step_responses,
            root_cause=root_cause,
            corrective_actions=corrective_actions,
            lessons_learned=lessons_learned,
            resolution_status="resolved",
            resolution_date=datetime.utcnow(),
            embedding_status="pending"
        )

        # Requirement 20.3: Index to Qdrant (Background Task)
        # We index the problem description and lessons learned for semantic search
        index_text = f"Problem: {record.problem_description}\nDersler: {record.lessons_learned}"
        metadata = {
            "title": record.title,
            "methodology": record.methodology,
            "user_id": str(record.user_id)
        }
        
        # Trigger Celery task
        generate_embedding_task.delay(str(record.id), index_text, metadata)

        return {
            "record_id": str(record.id),
            "title": record.title,
            "lessons_learned": record.lessons_learned,
            "status": "published"
        }
