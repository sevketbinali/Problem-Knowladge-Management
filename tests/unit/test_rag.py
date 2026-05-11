import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st

from src.infrastructure.services.rag_engine import RAGEngine

@pytest.fixture
def rag_engine():
    embedding_service = AsyncMock()
    embedding_service.generate_embedding.return_value = [0.1] * 768
    
    with patch("src.infrastructure.services.rag_engine.QdrantRepository") as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        mock_repo.search_similar = AsyncMock(return_value=[])
        mock_repo.index_record = AsyncMock()
        engine = RAGEngine(embedding_service)
        engine.repository = mock_repo # Ensure it uses our mock
        return engine

@pytest.mark.asyncio
async def test_rag_search_sorting(rag_engine):
    """Requirement 8.1: RAG search results should be returned with scores."""
    rag_engine.repository.search_similar.return_value = [
        {"id": str(uuid.uuid4()), "score": 0.95, "payload": {"title": "P1"}},
        {"id": str(uuid.uuid4()), "score": 0.85, "payload": {"title": "P2"}}
    ]
    
    results = await rag_engine.search_similar("test query", limit=5)
    
    assert len(results) == 2
    assert results[0]["score"] == 0.95
    assert results[1]["score"] == 0.85

@pytest.mark.asyncio
async def test_rag_degraded_mode(rag_engine):
    """Requirement 23.1: RAG engine should enter degraded mode after 3 errors."""
    rag_engine.repository.search_similar.side_effect = Exception("Connection Failed")
    
    # 1st error
    results = await rag_engine.search_similar("q")
    assert results == [] # Should continue with empty results
    
    # 2nd error
    await rag_engine.search_similar("q")
    # 3rd error
    await rag_engine.search_similar("q")
    
    assert rag_engine._degraded_mode is True
    
    # Now it should not even call the repository
    rag_engine.repository.search_similar.reset_mock()
    results = await rag_engine.search_similar("q")
    assert results == []
    rag_engine.repository.search_similar.assert_not_called()

@given(st.text(min_size=20, max_size=1000))
@pytest.mark.asyncio
async def test_rag_result_count_limit_property(query):
    """Requirement 1.6: RAG result count limit property test."""
    embedding_service = AsyncMock()
    embedding_service.generate_embedding.return_value = [0.1] * 768
    
    with patch("src.infrastructure.services.rag_engine.QdrantRepository") as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        # Mocking search to return up to 5 results
        mock_repo.search_similar = AsyncMock(return_value=[{"id": str(i)} for i in range(5)])
        
        engine = RAGEngine(embedding_service)
        engine.repository = mock_repo
        
        results = await engine.search_similar(query, limit=5)
        assert len(results) <= 5
