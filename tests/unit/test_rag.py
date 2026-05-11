import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from hypothesis import given, strategies as st

from src.infrastructure.services.rag_engine import RAGEngine

@pytest.mark.asyncio
async def test_rag_search_sorting():
    """Requirement 8.1: RAG search results should be returned with scores."""
    
    # Mock EmbeddingService
    embedding_service = AsyncMock()
    embedding_service.generate_embedding.return_value = [0.1] * 768
    
    # Mock QdrantClient
    mock_client = MagicMock()
    # Mock search results - already sorted by Qdrant usually, but we check our mapping
    mock_hit1 = MagicMock()
    mock_hit1.id = str(uuid.uuid4())
    mock_hit1.score = 0.95
    mock_hit1.payload = {"title": "Similar Problem 1"}
    
    mock_hit2 = MagicMock()
    mock_hit2.id = str(uuid.uuid4())
    mock_hit2.score = 0.85
    mock_hit2.payload = {"title": "Similar Problem 2"}
    
    mock_client.search.return_value = [mock_hit1, mock_hit2]
    mock_client.get_collections.return_value.collections = [MagicMock(name="problem_records")]
    
    # Patch QdrantClient in RAGEngine
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.infrastructure.services.rag_engine.QdrantClient", lambda **kwargs: mock_client)
        
        engine = RAGEngine(embedding_service)
        results = await engine.search_similar("test query", limit=5)
        
        assert len(results) == 2
        assert results[0]["score"] == 0.95
        assert results[1]["score"] == 0.85
        assert results[0]["score"] >= results[1]["score"]
        assert results[0]["payload"]["title"] == "Similar Problem 1"

@pytest.mark.asyncio
async def test_rag_upsert_calls_embedding():
    """Requirement 6.2: Upsert should generate embedding first."""
    embedding_service = AsyncMock()
    embedding_service.generate_embedding.return_value = [0.5] * 768
    
    mock_client = MagicMock()
    mock_client.get_collections.return_value.collections = [MagicMock(name="problem_records")]
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.infrastructure.services.rag_engine.QdrantClient", lambda **kwargs: mock_client)
        
        engine = RAGEngine(embedding_service)
        record_id = uuid.uuid4()
        await engine.upsert_record(record_id, "problem text", {"meta": "data"})
        
        embedding_service.generate_embedding.assert_called_once_with("problem text")
        mock_client.upsert.assert_called_once()
        # Check if the vector passed to upsert matches mock
        args, kwargs = mock_client.upsert.call_args
        assert kwargs["points"][0].vector == [0.5] * 768
