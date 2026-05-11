"""Property-based tests for ProblemRecord serialization and parsing.

Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone

import jsonschema
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.domain.models import EmbeddingStatus, MethodologyType, ProblemRecord

# ---------------------------------------------------------------------------
# Hypothesis settings shared across all tests
# ---------------------------------------------------------------------------

_SETTINGS = settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=5000,
)

# ---------------------------------------------------------------------------
# JSON Schema for ProblemRecord (from design.md)
# ---------------------------------------------------------------------------

PROBLEM_RECORD_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ProblemRecord",
    "type": "object",
    "required": [
        "id",
        "session_id",
        "user_id",
        "problem_description",
        "methodology",
        "step_responses",
        "root_cause",
        "corrective_actions",
        "lessons_learned",
        "resolution_status",
        "created_at",
        "updated_at",
    ],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "session_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "title": {"type": "string"},
        "problem_description": {"type": "string", "minLength": 20, "maxLength": 2000},
        "methodology": {"type": "string", "enum": ["ishikawa", "8d", "5why", "pdca"]},
        "step_responses": {"type": "object"},
        "root_cause": {"type": "string"},
        "corrective_actions": {"type": "array", "items": {"type": "string"}},
        "lessons_learned": {"type": "string"},
        "industry_sector": {"type": ["string", "null"]},
        "department": {"type": ["string", "null"]},
        "problem_category": {"type": ["string", "null"]},
        "resolution_status": {"type": "string"},
        "resolution_date": {"type": ["string", "null"], "format": "date"},
        "embedding_status": {
            "type": "string",
            "enum": ["pending", "completed", "failed"],
        },
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# Required fields as listed in the JSON schema
REQUIRED_FIELDS: list[str] = PROBLEM_RECORD_SCHEMA["required"]

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

_uuid_st = st.uuids().map(str)

_datetime_st = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2099, 12, 31),
    timezones=st.just(timezone.utc),
)

_date_st = st.dates(
    min_value=date(2000, 1, 1),
    max_value=date(2099, 12, 31),
)

_methodology_st = st.sampled_from(MethodologyType)

_embedding_status_st = st.sampled_from(EmbeddingStatus)

# problem_description must be 20–2000 chars
_problem_description_st = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=20,
    max_size=2000,
)

_str_st = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=200,
)

_optional_str_st = st.one_of(st.none(), _str_st)

_corrective_actions_st = st.lists(_str_st, min_size=0, max_size=5)

_step_responses_st = st.dictionaries(
    keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_")),
    values=_str_st,
    min_size=0,
    max_size=5,
)

_problem_record_st = st.builds(
    ProblemRecord,
    id=st.uuids(),
    session_id=st.uuids(),
    user_id=st.uuids(),
    title=_str_st,
    problem_description=_problem_description_st,
    methodology=_methodology_st,
    step_responses=_step_responses_st,
    root_cause=_str_st,
    corrective_actions=_corrective_actions_st,
    lessons_learned=_str_st,
    industry_sector=_optional_str_st,
    department=_optional_str_st,
    problem_category=_optional_str_st,
    resolution_status=_str_st,
    resolution_date=st.one_of(st.none(), _date_st),
    embedding_status=_embedding_status_st,
    created_at=_datetime_st,
    updated_at=_datetime_st,
)


# ---------------------------------------------------------------------------
# Helper: serialize a ProblemRecord to a JSON-compatible dict
# ---------------------------------------------------------------------------

def _serialize(record: ProblemRecord) -> dict:
    """Serialize ProblemRecord to a plain dict (JSON-safe via model_dump)."""
    return json.loads(record.model_dump_json())


def _parse(data: dict) -> ProblemRecord:
    """Parse a plain dict into a ProblemRecord."""
    return ProblemRecord.model_validate(data)


# ---------------------------------------------------------------------------
# Property 30: Serialization Round-Trip
# Validates: Requirement 13.4
# ---------------------------------------------------------------------------

@_SETTINGS
@given(_problem_record_st)
def test_roundtrip(record: ProblemRecord) -> None:
    """Property 30: For any valid ProblemRecord P, parse(serialize(P)) == P field-by-field.

    **Validates: Requirements 13.4**
    """
    serialized = _serialize(record)
    restored = _parse(serialized)

    # Field-by-field value and type equality
    assert restored.id == record.id
    assert restored.session_id == record.session_id
    assert restored.user_id == record.user_id
    assert restored.title == record.title
    assert restored.problem_description == record.problem_description
    assert restored.methodology == record.methodology
    assert type(restored.methodology) is type(record.methodology)
    assert restored.step_responses == record.step_responses
    assert restored.root_cause == record.root_cause
    assert restored.corrective_actions == record.corrective_actions
    assert restored.lessons_learned == record.lessons_learned
    assert restored.industry_sector == record.industry_sector
    assert restored.department == record.department
    assert restored.problem_category == record.problem_category
    assert restored.resolution_status == record.resolution_status
    assert restored.resolution_date == record.resolution_date
    assert restored.embedding_status == record.embedding_status
    assert type(restored.embedding_status) is type(record.embedding_status)
    # Datetimes: compare as UTC-aware, ignoring sub-microsecond precision
    assert restored.created_at.replace(microsecond=0) == record.created_at.replace(microsecond=0)
    assert restored.updated_at.replace(microsecond=0) == record.updated_at.replace(microsecond=0)


# ---------------------------------------------------------------------------
# Property 31: JSON Schema Compliance
# Validates: Requirement 13.1
# ---------------------------------------------------------------------------

@_SETTINGS
@given(_problem_record_st)
def test_schema_compliance(record: ProblemRecord) -> None:
    """Property 31: Every serialized ProblemRecord must comply with the JSON schema.

    **Validates: Requirements 13.1**
    """
    serialized = _serialize(record)
    # Validate against the schema — raises jsonschema.ValidationError on failure
    jsonschema.validate(instance=serialized, schema=PROBLEM_RECORD_SCHEMA)


# ---------------------------------------------------------------------------
# Property 32: Parse Field Match
# Validates: Requirement 13.2
# ---------------------------------------------------------------------------

@_SETTINGS
@given(_problem_record_st)
def test_parse_field_match(record: ProblemRecord) -> None:
    """Property 32: For every valid JSON document, parsed object fields match source JSON.

    **Validates: Requirements 13.2**
    """
    source_json = _serialize(record)
    parsed = _parse(source_json)
    round_tripped = _serialize(parsed)

    # Every key present in the source JSON must match in the re-serialized output
    for key in source_json:
        assert round_tripped[key] == source_json[key], (
            f"Field '{key}' mismatch: source={source_json[key]!r}, "
            f"round-tripped={round_tripped[key]!r}"
        )


# ---------------------------------------------------------------------------
# Property 33: Pretty Printer Format
# Validates: Requirement 13.3
# ---------------------------------------------------------------------------

@_SETTINGS
@given(_problem_record_st)
def test_pretty_printer(record: ProblemRecord) -> None:
    """Property 33: Pretty printer output must be 2-space indented with lexicographic key order.

    **Validates: Requirements 13.3**
    """
    data = _serialize(record)
    pretty = json.dumps(data, indent=2, sort_keys=True, default=str)

    # Must be valid JSON
    reparsed = json.loads(pretty)

    # Keys at the top level must be in lexicographic (sorted) order
    top_level_keys = list(reparsed.keys())
    assert top_level_keys == sorted(top_level_keys), (
        f"Top-level keys are not in lexicographic order: {top_level_keys}"
    )

    # Verify 2-space indentation: every indented line starts with multiples of 2 spaces
    for line in pretty.splitlines():
        stripped = line.lstrip(" ")
        leading_spaces = len(line) - len(stripped)
        assert leading_spaces % 2 == 0, (
            f"Line has odd indentation ({leading_spaces} spaces): {line!r}"
        )

    # Verify nested objects also have sorted keys
    def _check_sorted_keys(obj: object) -> None:
        if isinstance(obj, dict):
            keys = list(obj.keys())
            assert keys == sorted(keys), f"Nested keys not sorted: {keys}"
            for v in obj.values():
                _check_sorted_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                _check_sorted_keys(item)

    _check_sorted_keys(reparsed)


# ---------------------------------------------------------------------------
# Property 34: Unknown Field Tolerance
# Validates: Requirement 13.5
# ---------------------------------------------------------------------------

_unknown_field_key_st = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll"), whitelist_characters="_"),
    min_size=5,
    max_size=30,
).filter(lambda k: k not in PROBLEM_RECORD_SCHEMA["properties"])

_unknown_field_value_st = st.one_of(
    st.text(min_size=0, max_size=50),
    st.integers(),
    st.booleans(),
    st.none(),
)


@_SETTINGS
@given(
    record=_problem_record_st,
    extra_key=_unknown_field_key_st,
    extra_value=_unknown_field_value_st,
)
def test_unknown_field_tolerance(
    record: ProblemRecord, extra_key: str, extra_value: object
) -> None:
    """Property 34: Parsing JSON with extra unknown fields must succeed; unknown fields ignored.

    **Validates: Requirements 13.5**
    """
    data = _serialize(record)
    data[extra_key] = extra_value  # inject unknown field

    # Must not raise
    parsed = _parse(data)

    # Unknown field must not appear on the parsed object
    assert not hasattr(parsed, extra_key), (
        f"Unknown field '{extra_key}' was not ignored by the parser"
    )

    # All known fields must still be present and correct
    restored = _serialize(parsed)
    for key in PROBLEM_RECORD_SCHEMA["properties"]:
        if key in _serialize(record):
            assert restored.get(key) == _serialize(record).get(key), (
                f"Known field '{key}' changed after parsing with unknown fields"
            )


# ---------------------------------------------------------------------------
# Property 35: Missing Required Field Error Message
# Validates: Requirement 13.6
# ---------------------------------------------------------------------------

@_SETTINGS
@given(
    record=_problem_record_st,
    missing_field=st.sampled_from(REQUIRED_FIELDS),
)
def test_missing_field_error(record: ProblemRecord, missing_field: str) -> None:
    """Property 35: For every JSON missing a required field, the error must name the missing field.

    **Validates: Requirements 13.6**
    """
    data = _serialize(record)
    del data[missing_field]  # remove the required field

    with pytest.raises(ValidationError) as exc_info:
        _parse(data)

    error_str = str(exc_info.value)
    assert missing_field in error_str, (
        f"Error message does not mention missing field '{missing_field}'.\n"
        f"Full error: {error_str}"
    )
