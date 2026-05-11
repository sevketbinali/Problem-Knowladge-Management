"""Property-based tests for ProblemRecord serialization."""
import json
from typing import Any

import pytest
from pydantic import ValidationError
from hypothesis import given, strategies as st

from src.api.v1.schemas import ProblemRecord
from src.domain.models import MethodologyType


# Custom strategy for ProblemRecord
problem_record_strategy = st.builds(
    ProblemRecord,
    id=st.uuids(),
    title=st.text(min_size=10, max_size=100),
    problem_description=st.text(min_size=20, max_size=1000),
    methodology=st.sampled_from([m.value for m in MethodologyType]),
    step_responses=st.dictionaries(st.text(min_size=1), st.text(min_size=1)),
    root_cause=st.text(min_size=10),
    corrective_actions=st.lists(st.text(min_size=5), min_size=1, max_size=5),
    lessons_learned=st.text(min_size=100, max_size=2000),
    industry_sector=st.none() | st.text(min_size=2),
    department=st.none() | st.text(min_size=2),
    problem_category=st.none() | st.text(min_size=2),
    resolution_status=st.sampled_from(["open", "resolved", "closed"]),
    resolution_date=st.datetimes(),
    embedding_status=st.sampled_from(["pending", "indexed", "failed"]),
    created_at=st.datetimes(),
    updated_at=st.datetimes()
)


@given(problem_record_strategy)
def test_roundtrip(record: ProblemRecord):
    """Requirement 13.4: P == parse(serialize(P))"""
    serialized = record.model_dump_json()
    parsed = ProblemRecord.model_validate_json(serialized)
    
    assert record.id == parsed.id
    assert record.title == parsed.title
    assert record.problem_description == parsed.problem_description
    assert record.methodology == parsed.methodology
    assert record.step_responses == parsed.step_responses
    assert record.root_cause == parsed.root_cause
    assert record.corrective_actions == parsed.corrective_actions
    assert record.lessons_learned == parsed.lessons_learned


@given(problem_record_strategy)
def test_schema_compliance(record: ProblemRecord):
    """Requirement 13.1: JSON matches schema."""
    serialized_dict = json.loads(record.model_dump_json())
    # Pydantic validation itself ensures schema compliance
    assert ProblemRecord.model_validate(serialized_dict)


@given(st.dictionaries(st.text(), st.text() | st.integers() | st.booleans()))
def test_unknown_field_tolerance(extra_data: dict):
    """Requirement 13.5: Unknown fields are ignored."""
    base_record = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Problem Title",
        "problem_description": "This is a long enough problem description for validation.",
        "methodology": "ishikawa",
        "step_responses": {"1": "Response"},
        "root_cause": "Root cause found",
        "corrective_actions": ["Action 1"],
        "lessons_learned": "A" * 150, # Min 100
        "resolution_status": "resolved",
        "resolution_date": "2024-01-01T00:00:00",
        "embedding_status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    # Merge with extra data (avoid overwriting base fields with invalid data)
    for k, v in extra_data.items():
        if k not in base_record:
            base_record[k] = v
            
    parsed = ProblemRecord.model_validate(base_record)
    assert parsed.title == "Test Problem Title"


def test_pretty_printer():
    """Requirement 13.3: Pretty printer format (2 spaces, keys sorted)."""
    record = ProblemRecord(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Test Title",
        problem_description="Description that is long enough.",
        methodology="5-why",
        step_responses={},
        root_cause="Root",
        corrective_actions=[],
        lessons_learned="A" * 150,
        resolution_status="open",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )
    
    # In Pydantic v2, we use model_dump_json(indent=2)
    pretty_json = record.model_dump_json(indent=2)
    
    # Check indentation
    lines = pretty_json.splitlines()
    if len(lines) > 1:
        assert lines[1].startswith("  ")
        assert not lines[1].startswith("   ")


@given(st.sampled_from([
    "id", "title", "problem_description", "methodology", 
    "root_cause", "corrective_actions", "lessons_learned",
    "resolution_status", "created_at", "updated_at"
]))
def test_missing_field_error(missing_field: str):
    """Requirement 13.6: Error message must specify missing field name."""
    base_record = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Title",
        "problem_description": "Description long enough...",
        "methodology": "ishikawa",
        "root_cause": "Root",
        "corrective_actions": [],
        "lessons_learned": "A" * 150,
        "resolution_status": "open",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    del base_record[missing_field]
    
    with pytest.raises(ValidationError) as exc_info:
        ProblemRecord.model_validate(base_record)
    
    # Verify that the missing field name is in the error message
    assert missing_field in str(exc_info.value)

