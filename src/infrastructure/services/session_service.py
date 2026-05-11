"""Service for managing problem-solving sessions and methodology flows."""
import uuid
from typing import Any, Dict, List, Optional

from src.core.methodology import MethodologyEngine, MethodologyType
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
        first_step = self.engine.get_step(m_type, 0)
        
        return {
            "session_id": str(db_session.id),
            "methodology": methodology,
            "current_step": 0,
            "next_prompt": first_step.question if first_step else None,
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
        
        # Requirement 2.3: Handle followup questions
        # This logic would normally call LLM, but here we prepare for the state
        # In the actual implementation, submit_step_response might decide to 
        # either move to next step OR ask a followup if the response is vague.
        
        # For now, let's assume if response is < 20 chars, we ask followup (just for logic demonstration)
        needs_clarification = len(response) < 20 and db_session.followup_count < 3
        
        if needs_clarification:
            new_followup_count = db_session.followup_count + 1
            await self.repository.update_session(session_id, followup_count=new_followup_count)
            
            # Get followup from LLM
            followup_q = await self.llm.generate_clarification(response)
            
            return {
                "session_id": str(session_id),
                "current_step": db_session.current_step_index,
                "next_prompt": followup_q,
                "followup_count": new_followup_count,
                "can_proceed": new_followup_count >= 3,
                "status": "active"
            }

        # If no clarification needed or max followups reached, move to next step
        next_step_index = db_session.current_step_index + 1
        is_complete = self.engine.is_complete(m_type, next_step_index)
        
        # Reset followup count for next step
        update_data = {
            "step_responses": current_responses,
            "current_step_index": next_step_index,
            "followup_count": 0
        }
        
        if is_complete:
            update_data["status"] = "completed"
        
        await self.repository.update_session(session_id, **update_data)
        
        if is_complete:
            return {
                "session_id": str(session_id),
                "status": "completed",
                "message": "Metodoloji tamamlandı. Analiz raporu oluşturulabilir."
            }
        
        next_step = self.engine.get_step(m_type, next_step_index)
        
        return {
            "session_id": str(session_id),
            "current_step": next_step_index,
            "next_prompt": next_step.question if next_step else None,
            "followup_count": 0,
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
