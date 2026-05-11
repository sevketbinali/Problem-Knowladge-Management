import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from hypothesis import given, strategies as st

from src.infrastructure.services.session_service import SessionService
from src.core.methodology import MethodologyEngine, MethodologyType

@pytest.fixture
def session_service():
    repo = AsyncMock()
    engine = MethodologyEngine()
    llm = AsyncMock()
    return SessionService(repo, engine, llm)

def test_circular_logic_detection(session_service):
    """Requirement 11.3, 11.4: Circular logic detection logic."""
    prev_answers = [
        "Sensör arızalı",
        "Kablo bağlantısı kopuk"
    ]
    
    # 70%+ overlap
    assert session_service.detect_circular_logic("Sensör arızalı", prev_answers) is True
    # "Sensör arızalı" (2) and "Sensör arızalı" (2) -> 100%
    
    # < 70% overlap
    assert session_service.detect_circular_logic("Güç kaynağı problemi", prev_answers) is False
    assert session_service.detect_circular_logic("Yazılım hatası olabilir", prev_answers) is False

@pytest.mark.asyncio
async def test_5why_question_count_limits(session_service):
    """Requirement 4.3: 5 Why question count limits (3-7)."""
    session_id = uuid.uuid4()
    
    # Mock session for 5 Why
    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.methodology = "5why"
    mock_session.current_step_index = 2 # 3rd question (0, 1, 2)
    mock_session.step_responses = {"0": "Why 1 ans", "1": "Why 2 ans"}
    mock_session.followup_count = 0
    
    session_service.repository.get_session.return_value = mock_session
    session_service.llm.generate_next_why.return_value = "Neden?"
    
    # Submit 3rd answer
    result = await session_service.submit_step_response(session_id, "Answer 3")
    assert result["current_step"] == 3
    assert result["can_proceed"] is True # 3rd answer submitted, now we are at step 3, can proceed
    
    # Move to 7th answer
    mock_session.current_step_index = 6
    mock_session.step_responses = {str(i): f"Ans {i}" for i in range(6)}
    
    result = await session_service.submit_step_response(session_id, "Answer 7")
    assert result["status"] == "completed"
    assert "7. neden alındı" in result["message"]

@given(st.lists(st.text(min_size=5), min_size=2, max_size=5))
def test_circular_logic_property(prev_answers):
    """Property test for circular logic: identical text must be detected."""
    repo = AsyncMock()
    engine = MethodologyEngine()
    llm = AsyncMock()
    svc = SessionService(repo, engine, llm)
    
    # If we use the exact same answer as one of the previous ones
    for ans in prev_answers:
        assert svc.detect_circular_logic(ans, prev_answers) is True
