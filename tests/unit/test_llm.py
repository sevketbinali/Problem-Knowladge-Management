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
from hypothesis import given, strategies as st, settings, HealthCheck

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.text())
@pytest.mark.asyncio
async def test_lessons_structural_components(llm_service, text):
    """Requirement 7.4: Lessons Learned structural component control property test."""
    # We want to verify that regardless of what LLM returns, 
    # we have the 4 required components or placeholders.
    with patch("asyncio.to_thread", return_value=MagicMock(text=text)):
        result = await llm_service.generate_lessons_learned({})
        
        required = ["Kök Neden", "Düzeltici Eylemler", "Sonuç", "Önleyici Öneriler"]
        for item in required:
            assert item in result
