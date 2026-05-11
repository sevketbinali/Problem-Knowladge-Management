"""Pydantic schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


# Auth Schemas
class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Session Schemas
class SessionStart(BaseModel):
    problem_description: str = Field(..., min_length=20, max_length=2000)
    methodology: str

class SessionResponse(BaseModel):
    session_id: str
    methodology: Optional[str] = None
    current_step: Optional[int] = None
    next_prompt: Optional[str] = None
    total_steps: Optional[int] = None
    status: str = "active"
    can_proceed: Optional[bool] = None
    category_suggestion: Optional[str] = None
    error: Optional[str] = None
    similar_problems: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None

class StepResponse(BaseModel):
    response: str = Field(..., min_length=10)



# Analysis Schemas
class AnalysisReport(BaseModel):
    record_id: str
    title: str
    lessons_learned: str
    status: str


# Search Schemas
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=10, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10

class SearchResult(BaseModel):
    id: str
    score: float
    payload: Dict[str, Any]


# Knowledge Management Schemas
class ProblemRecord(BaseModel):
    id: uuid.UUID
    title: str
    problem_description: str
    methodology: str
    step_responses: Dict[str, Any]
    root_cause: str
    corrective_actions: List[str]
    lessons_learned: str
    industry_sector: Optional[str] = None
    department: Optional[str] = None
    problem_category: Optional[str] = None
    resolution_status: str
    resolution_date: Optional[datetime] = None
    embedding_status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WhyChain(BaseModel):
    questions: List[str]
    answers: List[str]
    root_cause: str

class IshikawaData(BaseModel):
    man: List[str]
    machine: List[str]
    method: List[str]
    material: List[str]
    measurement: List[str]
    environment: List[str]

class EightDReport(BaseModel):
    d1_team: str
    d2_problem: str
    d3_containment: str
    d4_root_cause: str
    d5_corrective: str
    d6_implementation: str
    d7_prevention: str
    d8_closure: str
