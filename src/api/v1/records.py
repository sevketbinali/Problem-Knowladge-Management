import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.dependencies import get_current_active_user, get_repository
from src.api.v1.schemas import APIResponse
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

router = APIRouter(prefix="/records", tags=["Problem Records"])

@router.get("", response_model=APIResponse[List[dict]])
async def list_records(
    q: str = None,
    department: str = None,
    methodology: str = None,
    tag: str = None,
    sort: str = "newest", # "newest" or "oldest"
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 3.3: List finalized problem records with filters."""
    # This would ideally be in the repository, but for speed I'll implement filter logic here or update repo
    records = await repo.search_records(
        query=q, 
        department=department, 
        methodology=methodology, 
        tag=tag,
        sort=sort,
        skip=skip, 
        limit=limit
    )
    data = [
        {
            "id": str(r.id),
            "title": r.title,
            "problem_description": r.problem_description,
            "department": r.department,
            "methodology": r.methodology,
            "root_cause": r.root_cause,
            "lessons_learned": r.lessons_learned,
            "tags": r.tags or [],
            "resolution_status": r.resolution_status,
            "created_by": r.user.full_name if r.user else "Bilinmiyor",
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat()
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
        "department": record.department,
        "problem_description": record.problem_description,
        "methodology": record.methodology,
        "step_responses": record.step_responses,
        "root_cause": record.root_cause,
        "corrective_actions": record.corrective_actions,
        "lessons_learned": record.lessons_learned,
        "tags": record.tags or [],
        "status": record.resolution_status,
        "created_by": record.user.full_name if record.user else "Bilinmiyor",
        "created_at": record.created_at.isoformat()
    }
    return APIResponse(data=data)
