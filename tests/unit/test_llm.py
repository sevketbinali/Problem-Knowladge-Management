import pytest
from unittest.mock import MagicMock, patch
from src.infrastructure.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    with patch("google.genai.Client"):
        return LLMService()

@pytest.mark.asyncio
async def test_llm_fallback_on_error(llm_service):
    """Requirement 14.1: Fallback strategy when LLM fails."""
    # Simulate API error
    with patch("asyncio.to_thread", side_effect=Exception("API Down")):
        result = await llm_service.generate_clarification("test")
        assert result == "Problem hakkında daha fazla detay verebilir misiniz?"
        
        result = await llm_service.generate_next_why("test", [])
        assert result == "Bu durumun kök nedeni nedir?"

@pytest.mark.asyncio
async def test_lessons_learned_placeholder(llm_service):
    """Requirement 14.2: Placeholder fallback for lessons learned."""
    with patch("asyncio.to_thread", return_value=MagicMock(text="")):
        result = await llm_service.generate_lessons_learned({})
        assert "Placeholder" in result
        assert "Kök Neden" in result
