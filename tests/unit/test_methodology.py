import pytest
from src.core.methodology import MethodologyEngine, MethodologyType

def test_get_template_valid():
    """Test getting a valid template."""
    template = MethodologyEngine.get_template(MethodologyType.ISHIKAWA)
    assert template.methodology_type == MethodologyType.ISHIKAWA
    assert len(template.steps) == 6

def test_get_template_invalid():
    """Test getting an invalid template throws error."""
    with pytest.raises(ValueError):
        MethodologyEngine.get_template("non_existent")

def test_get_step():
    """Test getting a specific step."""
    step = MethodologyEngine.get_step(MethodologyType.FIVE_WHY, 0)
    assert step.name == "Why 1"
    assert "neden oluşuyor" in step.question

def test_is_complete():
    """Test completion logic."""
    # 5 Why has 5 steps defined in template (default)
    assert MethodologyEngine.is_complete(MethodologyType.FIVE_WHY, 4) is False
    assert MethodologyEngine.is_complete(MethodologyType.FIVE_WHY, 5) is True

def test_eight_d_steps():
    """Verify 8D steps are correct."""
    template = MethodologyEngine.get_template(MethodologyType.EIGHT_D)
    assert len(template.steps) == 8
    assert template.steps[0].name == "D1"
    assert template.steps[7].name == "D8"
