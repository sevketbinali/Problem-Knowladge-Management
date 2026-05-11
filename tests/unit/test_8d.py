import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from src.infrastructure.services.session_service import SessionService
from src.core.methodology import MethodologyEngine, MethodologyType

@pytest.fixture
def session_service():
    repo = AsyncMock()
    engine = MethodologyEngine()
    llm = AsyncMock()
    return SessionService(repo, engine, llm)

@pytest.mark.asyncio
async def test_8d_completion_requirement(session_service):
    """Requirement 2.6, 5.5: 8D completion requires all steps to be filled (>10 chars)."""
    session_id = uuid.uuid4()
    
    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.methodology = "8d"
    mock_session.current_step_index = 7 # Last step (D8)
    mock_session.followup_count = 0
    # Simulate D1-D7 filled, but D8 empty/short
    mock_session.step_responses = {str(i): "Filled with enough text" for i in range(7)}
    
    session_service.repository.get_session.return_value = mock_session
    session_service.llm.is_response_vague.return_value = False
    
    # Try to submit empty D8
    result = await session_service.submit_step_response(session_id, "Too short")
    assert "error" in result
    assert "D8" in result["error"]
    
    # Try to submit valid D8
    result = await session_service.submit_step_response(session_id, "This is a valid long enough closing response.")
    assert result["status"] == "completed"
    
    # Verify repository was called with formatted 8D report
    args, kwargs = session_service.repository.update_session.call_args
    assert "d1_team" in kwargs["step_responses"]
    assert "d8_closure" in kwargs["step_responses"]
