"""Unit tests for domain models.

Validates: Requirements 6.1, 11.2, 13.1
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from src.domain.models import (
    APIResponse,
    EightDReport,
    EmbeddingStatus,
    ErrorDetail,
    IshikawaData,
    MethodologyType,
    ProblemRecord,
    SessionStatus,
    WhyChain,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)
_UUID = uuid.uuid4()


def _valid_record(**overrides) -> dict:
    base = {
        "id": _UUID,
        "session_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "title": "Conveyor belt failure",
        "problem_description": "The conveyor belt stops unexpectedly during production shifts.",
        "methodology": MethodologyType.ISHIKAWA,
        "step_responses": {"step1": "answer1"},
        "root_cause": "Worn motor bearings",
        "corrective_actions": ["Replace bearings", "Schedule preventive maintenance"],
        "lessons_learned": "Regular inspection intervals prevent unplanned downtime.",
        "resolution_status": "resolved",
        "embedding_status": EmbeddingStatus.PENDING,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestEnums:
    def test_methodology_type_values(self):
        assert MethodologyType.ISHIKAWA == "ishikawa"
        assert MethodologyType.EIGHT_D == "8d"
        assert MethodologyType.FIVE_WHY == "5why"
        assert MethodologyType.PDCA == "pdca"

    def test_session_status_values(self):
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.FINALIZED == "finalized"
        assert SessionStatus.CANCELLED == "cancelled"

    def test_embedding_status_values(self):
        assert EmbeddingStatus.PENDING == "pending"
        assert EmbeddingStatus.COMPLETED == "completed"
        assert EmbeddingStatus.FAILED == "failed"

    def test_invalid_methodology_raises(self):
        with pytest.raises(ValidationError):
            ProblemRecord(**_valid_record(methodology="unknown"))


# ---------------------------------------------------------------------------
# ProblemRecord – valid inputs
# ---------------------------------------------------------------------------


class TestProblemRecordValid:
    def test_minimal_valid_record(self):
        record = ProblemRecord(**_valid_record())
        assert record.title == "Conveyor belt failure"
        assert record.methodology == MethodologyType.ISHIKAWA

    def test_optional_fields_default_to_none(self):
        record = ProblemRecord(**_valid_record())
        assert record.industry_sector is None
        assert record.department is None
        assert record.problem_category is None
        assert record.resolution_date is None

    def test_optional_fields_accepted_when_provided(self):
        record = ProblemRecord(
            **_valid_record(
                industry_sector="automotive",
                department="production",
                problem_category="mechanical",
                resolution_date=date(2024, 1, 15),
            )
        )
        assert record.industry_sector == "automotive"
        assert record.resolution_date == date(2024, 1, 15)

    def test_unknown_fields_are_ignored(self):
        """Req 13.5 – extra fields must be silently dropped."""
        data = _valid_record()
        data["unknown_field"] = "should be ignored"
        record = ProblemRecord(**data)
        assert not hasattr(record, "unknown_field")

    def test_methodology_accepts_string_value(self):
        record = ProblemRecord(**_valid_record(methodology="8d"))
        assert record.methodology == MethodologyType.EIGHT_D


# ---------------------------------------------------------------------------
# ProblemRecord – invalid inputs (ValidationError expected)
# ---------------------------------------------------------------------------


class TestProblemRecordInvalid:
    def test_problem_description_too_short(self):
        """Req 1.3 – description < 20 chars must fail."""
        with pytest.raises(ValidationError) as exc_info:
            ProblemRecord(**_valid_record(problem_description="Too short"))
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("problem_description",) for e in errors)

    def test_problem_description_too_long(self):
        """Req 1.4 – description > 2000 chars must fail."""
        with pytest.raises(ValidationError) as exc_info:
            ProblemRecord(**_valid_record(problem_description="x" * 2001))
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("problem_description",) for e in errors)

    def test_problem_description_exactly_20_chars_is_valid(self):
        record = ProblemRecord(**_valid_record(problem_description="a" * 20))
        assert len(record.problem_description) == 20

    def test_problem_description_exactly_2000_chars_is_valid(self):
        record = ProblemRecord(**_valid_record(problem_description="a" * 2000))
        assert len(record.problem_description) == 2000

    def test_missing_required_field_raises(self):
        """Req 13.6 – missing mandatory field must raise with field name."""
        data = _valid_record()
        del data["root_cause"]
        with pytest.raises(ValidationError) as exc_info:
            ProblemRecord(**data)
        error_str = str(exc_info.value)
        assert "root_cause" in error_str

    def test_invalid_uuid_raises(self):
        with pytest.raises(ValidationError):
            ProblemRecord(**_valid_record(id="not-a-uuid"))

    def test_invalid_embedding_status_raises(self):
        with pytest.raises(ValidationError):
            ProblemRecord(**_valid_record(embedding_status="unknown_status"))


# ---------------------------------------------------------------------------
# IshikawaData
# ---------------------------------------------------------------------------


class TestIshikawaData:
    def test_valid_ishikawa(self):
        data = IshikawaData(
            man=["Operator fatigue"],
            machine=["Worn bearings"],
            method=["No SOP"],
            material=["Low-grade steel"],
            measurement=["Calibration drift"],
            environment=["High humidity"],
        )
        assert len(data.man) == 1

    def test_empty_lists_accepted(self):
        data = IshikawaData(
            man=[], machine=[], method=[], material=[], measurement=[], environment=[]
        )
        assert data.man == []

    def test_missing_category_raises(self):
        with pytest.raises(ValidationError):
            IshikawaData(man=["cause"], machine=[], method=[], material=[], measurement=[])


# ---------------------------------------------------------------------------
# WhyChain
# ---------------------------------------------------------------------------


class TestWhyChain:
    def test_valid_why_chain(self):
        chain = WhyChain(
            questions=["Why did it stop?", "Why did the motor overheat?"],
            answers=["Motor overheated", "Bearings were worn"],
            root_cause="Lack of preventive maintenance",
        )
        assert chain.root_cause == "Lack of preventive maintenance"

    def test_missing_root_cause_raises(self):
        with pytest.raises(ValidationError):
            WhyChain(questions=["Why?"], answers=["Because"])


# ---------------------------------------------------------------------------
# EightDReport
# ---------------------------------------------------------------------------


class TestEightDReport:
    def test_valid_8d_report(self):
        report = EightDReport(
            d1_team="Quality team",
            d2_problem="Belt stops",
            d3_containment="Manual override",
            d4_root_cause="Worn bearings",
            d5_corrective="Replace bearings",
            d6_implementation="Completed 2024-01-10",
            d7_prevention="Monthly inspection",
            d8_closure="Verified and closed",
        )
        assert report.d1_team == "Quality team"

    def test_missing_discipline_raises(self):
        with pytest.raises(ValidationError):
            EightDReport(
                d1_team="Team",
                d2_problem="Problem",
                d3_containment="Containment",
                d4_root_cause="Root cause",
                d5_corrective="Corrective",
                d6_implementation="Implementation",
                d7_prevention="Prevention",
                # d8_closure missing
            )


# ---------------------------------------------------------------------------
# APIResponse envelope
# ---------------------------------------------------------------------------


class TestAPIResponse:
    def test_success_envelope(self):
        """Req 11.2 – success: data populated, error null."""
        resp: APIResponse[dict] = APIResponse(
            status="success", data={"key": "value"}, error=None
        )
        assert resp.status == "success"
        assert resp.data == {"key": "value"}
        assert resp.error is None

    def test_error_envelope(self):
        """Req 11.2 – error: data null, error populated."""
        detail = ErrorDetail(code="VALIDATION_ERROR", message="Field too short")
        resp: APIResponse[None] = APIResponse(status="error", data=None, error=detail)
        assert resp.status == "error"
        assert resp.data is None
        assert resp.error.code == "VALIDATION_ERROR"

    def test_generic_with_problem_record(self):
        record = ProblemRecord(**_valid_record())
        resp: APIResponse[ProblemRecord] = APIResponse(
            status="success", data=record, error=None
        )
        assert resp.data.title == "Conveyor belt failure"

    def test_error_detail_missing_field_raises(self):
        with pytest.raises(ValidationError):
            ErrorDetail(code="ERR")  # message is missing
