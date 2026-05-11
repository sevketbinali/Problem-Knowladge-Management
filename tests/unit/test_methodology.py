"""Unit tests for MethodologyEngine."""
import pytest
from src.domain.methodologies import MethodologyEngine
from src.domain.models import MethodologyType

def test_methodology_engine_templates():
    engine = MethodologyEngine()
    
    # Test step counts
    assert engine.get_step_count(MethodologyType.ISHIKAWA) == 6
    assert engine.get_step_count(MethodologyType.EIGHT_D) == 8
    assert engine.get_step_count(MethodologyType.FIVE_WHY) == 5
    assert engine.get_step_count(MethodologyType.PDCA) == 4

def test_methodology_is_complete():
    engine = MethodologyEngine()
    
    # Ishikawa case
    responses = {str(i): "response" for i in range(6)}
    assert engine.is_complete(MethodologyType.ISHIKAWA, responses) is True
    
    responses_incomplete = {str(i): "response" for i in range(5)}
    assert engine.is_complete(MethodologyType.ISHIKAWA, responses_incomplete) is False

def test_get_step_prompt():
    engine = MethodologyEngine()
    template = engine.get_template(MethodologyType.ISHIKAWA)
    
    assert "Man" in template.get_step_prompt(0)
    assert "Machine" in template.get_step_prompt(1)
