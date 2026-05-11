import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.dependencies import get_current_active_user, get_repository
from src.api.v1.schemas import APIResponse
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

router = APIRouter(prefix="/records", tags=["Problem Records"])

@router.get("/", response_model=APIResponse[List[dict]])
async def list_records(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 3.3: List finalized problem records."""
    records = await repo.list_records(skip=skip, limit=limit)
    data = [
        {
            "id": str(r.id),
            "title": r.title,
            "methodology": r.methodology,
            "root_cause": r.root_cause,
            "lessons_learned": r.lessons_learned,
            "status": r.status,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]
    return APIResponse(data=data)

@router.get("/{record_id}", response_model=APIResponse[dict])
async def get_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Retrieve full details of a specific problem record."""
    record = await repo.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    data = {
        "id": str(record.id),
        "title": record.title,
        "problem_description": record.problem_description,
        "methodology": record.methodology,
        "step_responses": record.step_responses,
        "root_cause": record.root_cause,
        "corrective_actions": record.corrective_actions,
        "lessons_learned": record.lessons_learned,
        "status": record.status,
        "created_at": record.created_at.isoformat()
    }
    return APIResponse(data=data)
