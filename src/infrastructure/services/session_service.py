"""Service for managing problem-solving sessions and methodology flows."""
import uuid
from typing import Any, Dict, List, Optional

from src.domain.methodologies import MethodologyEngine
from src.domain.models import MethodologyType
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.llm_service import LLMService


class SessionService:
    def __init__(
        self, 
        repository: PostgreSQLRepository, 
        methodology_engine: MethodologyEngine,
        llm_service: LLMService
    ):
        self.repository = repository
        self.engine = methodology_engine
        self.llm = llm_service

    async def start_session(self, user_id: uuid.UUID, problem_description: str, methodology: str) -> Dict[str, Any]:
        """Start a new problem-solving session."""
        # Convert string to MethodologyType enum
        m_type = MethodologyType(methodology)
        
        # Create session in DB
        db_session = await self.repository.create_session(
            user_id=user_id,
            problem_description=problem_description,
            methodology=methodology
        )
        
        template = self.engine.get_template(m_type)
        first_step_prompt = template.get_step_prompt(0)
        
        return {
            "session_id": str(db_session.id),
            "methodology": methodology,
            "current_step": 0,
            "next_prompt": first_step_prompt,
            "total_steps": len(template.steps)
        }

    async def submit_step_response(self, session_id: uuid.UUID, response: str) -> Dict[str, Any]:
        """Submit response for the current step and get the next prompt."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
        
        m_type = MethodologyType(db_session.methodology)
        template = self.engine.get_template(m_type)
        
        # Save response
        current_responses = db_session.step_responses or {}
        current_responses[str(db_session.current_step_index)] = response
        
        # Increment step
        next_step_index = db_session.current_step_index + 1
        
        # Update DB
        update_data = {
            "step_responses": current_responses,
            "current_step_index": next_step_index
        }
        
        # Requirement 19.1: Check if complete
        is_complete = next_step_index >= len(template.steps)
        if is_complete:
            update_data["status"] = "completed"
        
        await self.repository.update_session(session_id, **update_data)
        
        if is_complete:
            return {
                "session_id": str(session_id),
                "status": "completed",
                "message": "Methodoloji tamamlandı. Analiz raporu oluşturulabilir."
            }
        
        next_prompt = template.get_step_prompt(next_step_index)
        
        return {
            "session_id": str(session_id),
            "current_step": next_step_index,
            "next_prompt": next_prompt,
            "status": "active"
        }

    async def step_back(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """Requirement 19.3: Step back logic."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
        
        if db_session.current_step_index == 0:
            return {
                "session_id": str(session_id),
                "current_step": 0,
                "message": "İlk adımdasınız, daha geriye gidilemez."
            }
        
        prev_step_index = db_session.current_step_index - 1
        
        # Update DB
        await self.repository.update_session(session_id, current_step_index=prev_step_index)
        
        m_type = MethodologyType(db_session.methodology)
        template = self.engine.get_template(m_type)
        prev_prompt = template.get_step_prompt(prev_step_index)
        
        return {
            "session_id": str(session_id),
            "current_step": prev_step_index,
            "next_prompt": prev_prompt
        }

    async def get_clarification_question(self, session_id: uuid.UUID) -> str:
        """Requirement 19.4: LLM follow-up question."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
            
        return await self.llm.generate_clarification(db_session.problem_description)
