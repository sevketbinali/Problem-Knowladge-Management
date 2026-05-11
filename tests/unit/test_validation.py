"""Property-based tests for domain validators.

Validates: Requirements 1.1, 1.3, 1.4, 2.2, 3.2, 7.1, 7.3, 8.1, 8.7
"""
import pytest
from hypothesis import given, strategies as st

from src.core.validators import (
    validate_problem_description,
    validate_step_response,
    validate_search_query,
    validate_lessons_learned,
    validate_ishikawa_cause,
    validate_ishikawa_structure,
    validate_why_chain
)


@given(st.text(min_size=0, max_size=3000))
def test_problem_description_length(text: str) -> None:
    """Property 1: Problem description length validation (20-2000 chars)."""
    if 20 <= len(text) <= 2000:
        validate_problem_description(text)  # Should not raise
    else:
        with pytest.raises(ValueError):
            validate_problem_description(text)


@given(st.text(min_size=0, max_size=1000))
def test_step_response_min_length(text: str) -> None:
    """Property 4: Step response minimum length validation (>=10 chars)."""
    if len(text) >= 10:
        validate_step_response(text)
    else:
        with pytest.raises(ValueError):
            validate_step_response(text)


@given(st.text(min_size=0, max_size=600))
def test_search_query_length(text: str) -> None:
    """Validate search query length (10-500 chars)."""
    if 10 <= len(text) <= 500:
        validate_search_query(text)
    else:
        with pytest.raises(ValueError):
            validate_search_query(text)


@given(st.lists(st.text(min_size=1), min_size=0, max_size=600))
def test_lessons_learned_word_count(word_list: list[str]) -> None:
    """Property 17: Lessons learned word count validation (100-500 words)."""
    text = " ".join(word_list)
    # Note: text.split() might not be exactly len(word_list) if words have spaces
    # but for property testing this is close enough to exercise the logic.
    actual_word_count = len(text.split())
    
    if 100 <= actual_word_count <= 500:
        validate_lessons_learned(text)
    else:
        with pytest.raises(ValueError):
            validate_lessons_learned(text)


@given(st.text(min_size=0, max_size=600))
def test_ishikawa_cause_validation(text: str) -> None:
    """Property 8: Ishikawa cause length validation (1-500 chars)."""
    if 1 <= len(text) <= 500:
        validate_ishikawa_cause(text)
    else:
        with pytest.raises(ValueError):
            validate_ishikawa_cause(text)


@given(st.dictionaries(st.text(), st.text()))
def test_ishikawa_structure_validation(data: dict) -> None:
    """Property 11.2: Ishikawa structure validation."""
    required = {"Human", "Machine", "Material", "Method", "Measurement", "Environment"}
    if required.issubset(data.keys()):
        validate_ishikawa_structure(data)
    else:
        with pytest.raises(ValueError):
            validate_ishikawa_structure(data)


@given(st.lists(st.text()))
def test_why_chain_validation(chain: list) -> None:
    """Property 11.3: Why chain length validation (exactly 5)."""
    if len(chain) == 5:
        validate_why_chain(chain)
    else:
        with pytest.raises(ValueError):
            validate_why_chain(chain)

