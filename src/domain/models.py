"""Domain models for the Problem Knowledge Management System.

Validates: Requirements 6.1, 11.2, 13.1
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MethodologyType(str, Enum):
    """Supported problem-solving methodologies."""

    ISHIKAWA = "ishikawa"
    EIGHT_D = "8d"
    FIVE_WHY = "5why"
    PDCA = "pdca"


class SessionStatus(str, Enum):
    """Lifecycle states of a problem-solving session."""

    ACTIVE = "active"
    FINALIZED = "finalized"
    CANCELLED = "cancelled"


class EmbeddingStatus(str, Enum):
    """Vector-embedding pipeline states for a problem record."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Core domain models
# ---------------------------------------------------------------------------


class ProblemRecord(BaseModel):
    """Structured record produced when a session is finalized.

    Validates: Requirement 6.1 (all mandatory fields present),
               Requirement 13.1 (JSON schema compliance).
    """

    id: UUID
    session_id: UUID
    user_id: UUID
    title: str
    problem_description: str = Field(min_length=20, max_length=2000)
    methodology: MethodologyType
    step_responses: dict[str, Any]
    root_cause: str
    corrective_actions: list[str]
    lessons_learned: str
    industry_sector: str | None = None
    department: str | None = None
    problem_category: str | None = None
    resolution_status: str
    resolution_date: date | None = None
    embedding_status: EmbeddingStatus = EmbeddingStatus.PENDING
    created_at: datetime
    updated_at: datetime

    model_config = {"extra": "ignore"}  # Req 13.5 – unknown fields are silently dropped


class IshikawaData(BaseModel):
    """Six-category Ishikawa (fishbone) cause data."""

    man: list[str]
    machine: list[str]
    method: list[str]
    material: list[str]
    measurement: list[str]
    environment: list[str]


class WhyChain(BaseModel):
    """5-Why question/answer chain with confirmed root cause."""

    questions: list[str]
    answers: list[str]
    root_cause: str


class EightDReport(BaseModel):
    """Eight-discipline structured report."""

    d1_team: str
    d2_problem: str
    d3_containment: str
    d4_root_cause: str
    d5_corrective: str
    d6_implementation: str
    d7_prevention: str
    d8_closure: str


# ---------------------------------------------------------------------------
# API envelope
# ---------------------------------------------------------------------------

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error payload included in error responses.

    Validates: Requirement 11.2
    """

    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    """Uniform JSON envelope for every API response.

    Invariant: exactly one of ``data`` / ``error`` is non-null.
    Validates: Requirement 11.2
    """

    status: str  # "success" | "error"
    data: T | None = None
    error: ErrorDetail | None = None
