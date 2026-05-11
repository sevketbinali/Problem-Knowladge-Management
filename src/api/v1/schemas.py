"""Pydantic schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
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
    methodology: str
    current_step: int
    next_prompt: Optional[str] = None
    total_steps: int
    status: str = "active"
    suggestions: Optional[List[str]] = None

class StepResponse(BaseModel):
    response: str = Field(..., min_length=10)
    suggestions: Optional[List[str]] = None



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

