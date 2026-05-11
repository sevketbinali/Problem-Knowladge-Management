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
async def test_step_back_logic(session_service):
    """Requirement 2.5: Step back logic."""
    session_id = uuid.uuid4()
    
    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.methodology = "ishikawa"
    mock_session.current_step_index = 1
    mock_session.step_responses = {"0": "Initial response"}
    
    session_service.repository.get_session.return_value = mock_session
    
    result = await session_service.step_back(session_id)
    assert result["current_step"] == 0
    assert result["previous_response"] == "Initial response"
    
    # Try to step back from step 0
    mock_session.current_step_index = 0
    with pytest.raises(ValueError, match="Cannot step back"):
        await session_service.step_back(session_id)

@pytest.mark.asyncio
async def test_session_id_uniqueness(session_service):
    """Requirement 1.5: Verify session creation calls repo which generates unique IDs."""
    user_id = uuid.uuid4()
    
    session_service.repository.create_session.side_effect = [
        MagicMock(id=uuid.uuid4()),
        MagicMock(id=uuid.uuid4())
    ]
    
    s1 = await session_service.start_session(user_id, "Problem 1", "5why")
    s2 = await session_service.start_session(user_id, "Problem 2", "5why")
    
    assert s1["session_id"] != s2["session_id"]

@pytest.mark.asyncio
async def test_session_start_calls_rag(session_service):
    """Requirement 1.6: System should search for similar problems at start."""
    user_id = uuid.uuid4()
    
    session_service.rag = AsyncMock()
    session_service.rag.search_similar.return_value = [{"id": "1", "score": 0.9}]
    session_service.repository.create_session.return_value = MagicMock(id=uuid.uuid4())
    
    result = await session_service.start_session(user_id, "Some problem description", "5why")
    
    assert len(result["similar_problems"]) == 1
    session_service.rag.search_similar.assert_called_once_with("Some problem description", limit=5)
from hypothesis import given, strategies as st

@given(st.integers(min_value=2, max_value=20))
@pytest.mark.asyncio
async def test_session_id_uniqueness_property(n):
    """Requirement 1.5: N concurrent session requests result in N unique UUIDs."""
    repo = AsyncMock()
    engine = MethodologyEngine()
    llm = AsyncMock()
    svc = SessionService(repo, engine, llm)
    
    user_id = uuid.uuid4()
    ids = [uuid.uuid4() for _ in range(n)]
    repo.create_session.side_effect = [MagicMock(id=i) for i in ids]
    
    results = []
    for _ in range(n):
        res = await svc.start_session(user_id, "Problem description long enough", "5why")
        results.append(res["session_id"])
        
    assert len(set(results)) == n

@given(st.lists(st.text(min_size=10), min_size=2, max_size=5))
@pytest.mark.asyncio
async def test_step_back_roundtrip(responses):
    """Requirement 2.5: Step back round-trip property test."""
    repo = AsyncMock()
    engine = MethodologyEngine()
    llm = AsyncMock()
    svc = SessionService(repo, engine, llm)
    
    session_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.methodology = "ishikawa"
    mock_session.current_step_index = len(responses) - 1
    mock_session.step_responses = {str(i): resp for i, resp in enumerate(responses)}
    
    repo.get_session.return_value = mock_session
    
    result = await svc.step_back(session_id)
    prev_idx = len(responses) - 2
    assert result["current_step"] == prev_idx
    assert result["previous_response"] == responses[prev_idx]
