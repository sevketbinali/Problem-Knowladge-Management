import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from hypothesis import given, strategies as st

from src.infrastructure.services.session_service import SessionService
from src.core.methodology import MethodologyEngine, MethodologyType

@pytest.mark.asyncio
async def test_followup_question_limit():
    """Requirement 2.3: Follow-up question limit test (Property-based)."""
    
    # Mock Repository
    repo = AsyncMock()
    # Mock LLM
    llm = AsyncMock()
    llm.generate_clarification.return_value = "Can you provide more detail?"
    
    engine = MethodologyEngine()
    service = SessionService(repo, engine, llm)
    
    session_id = uuid.uuid4()
    
    # We will simulate multiple vague responses for the same step
    # and verify the followup_count behavior.
    
    for count in range(1, 5):
        # Setup mock session state
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.current_step_index = 0
        mock_session.followup_count = count - 1 if count <= 3 else 3
        mock_session.methodology = "ishikawa"
        mock_session.step_responses = {}
        
        repo.get_session.return_value = mock_session
        
        # Vague response
        response = "too short"
        
        result = await service.submit_step_response(session_id, response)
        
        if count <= 3:
            # Should stay on same step and increment followup
            assert result["current_step"] == 0
            assert result["followup_count"] == count
            if count == 3:
                assert result["can_proceed"] is True
        else:
            # On 4th vague response, it MUST move to next step (index 1)
            assert result["current_step"] == 1
            assert result["followup_count"] == 0 # Reset for next step
