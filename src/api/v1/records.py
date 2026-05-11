"""Records router for administrative management of problem records."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.dependencies import get_admin_user, get_current_active_user, get_repository
from src.api.v1.schemas import APIResponse, ProblemRecord
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

router = APIRouter(prefix="/records", tags=["Records Management"])


@router.get("/", response_model=APIResponse[List[ProblemRecord]])
async def list_records(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 9.1: List all finalized problem records with pagination."""
    records = await repo.list_records(skip=skip, limit=limit)
    return APIResponse(data=records)


@router.get("/{record_id}", response_model=APIResponse[ProblemRecord])
async def get_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 9.2: Get a specific problem record by ID."""
    record = await repo.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return APIResponse(data=record)


@router.put("/{record_id}", response_model=APIResponse[ProblemRecord])
async def update_record(
    record_id: uuid.UUID,
    update_data: dict, # Simplified for now, should use a schema
    current_user: User = Depends(get_admin_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 9.3: Update a record (Admin only)."""
    record = await repo.update_record(record_id, **update_data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Audit logging
    await repo.create_audit_log(
        user_id=current_user.id,
        operation="update",
        entity_type="problem_record",
        entity_id=record_id,
        after_values=update_data
    )
    
    return APIResponse(data=record)


@router.delete("/{record_id}", response_model=APIResponse[None])
async def delete_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_admin_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Requirement 9.4: Delete a record (Admin only)."""
    success = await repo.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Audit logging
    await repo.create_audit_log(
        user_id=current_user.id,
        operation="delete",
        entity_type="problem_record",
        entity_id=record_id
    )
    
    return APIResponse(data=None, message="Record deleted successfully")
