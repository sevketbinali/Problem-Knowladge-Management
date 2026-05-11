"""Session router for problem-solving flows."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.dependencies import get_current_active_user, get_repository, get_rag_engine
from src.api.v1.schemas import APIResponse, SessionResponse, SessionStart, StepResponse
from src.core.methodology import MethodologyEngine
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.llm_service import LLMService
from src.infrastructure.services.rag_engine import RAGEngine
from src.infrastructure.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Problem Sessions"])


def get_session_service(
    repo: PostgreSQLRepository = Depends(get_repository),
    rag: RAGEngine = Depends(get_rag_engine)
) -> SessionService:
    return SessionService(repo, MethodologyEngine(), LLMService(), rag)


@router.post("/", response_model=APIResponse[SessionResponse])
async def start_session(
    data: SessionStart,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    """Requirement 1.5, 1.6: Start a new problem-solving session."""
    try:
        result = await service.start_session(
            user_id=current_user.id,
            problem_description=data.problem_description,
            methodology=data.methodology
        )
        return APIResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=APIResponse[List[SessionResponse]])
async def list_sessions(
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """List all sessions for the current user."""
    sessions = await repo.list_sessions_for_user(current_user.id)
    data = [
        {
            "session_id": str(s.id),
            "methodology": s.methodology,
            "current_step": s.current_step_index,
            "status": s.status,
            "total_steps": 0
        }
        for s in sessions
    ]
    return APIResponse(data=data)


@router.get("/{session_id}", response_model=APIResponse[SessionResponse])
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    repo: PostgreSQLRepository = Depends(get_repository)
):
    """Retrieve details of a specific session."""
    session = await repo.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = {
        "session_id": str(session.id),
        "methodology": session.methodology,
        "current_step": session.current_step_index,
        "status": session.status,
        "total_steps": 0
    }
    return APIResponse(data=data)


@router.post("/{session_id}/steps", response_model=APIResponse[SessionResponse])
async def submit_step(
    session_id: uuid.UUID,
    data: StepResponse,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    """Requirement 2.1: Submit response for the current step."""
    try:
        result = await service.submit_step_response(session_id, data.response)
        return APIResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/back", response_model=APIResponse[SessionResponse])
async def step_back(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    """Requirement 2.5: Go back to the previous step."""
    try:
        result = await service.step_back(session_id)
        return APIResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/finalize", response_model=APIResponse[dict])
async def finalize_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    """Finalize the session and trigger report generation."""
    session = await service.repository.get_session(session_id)
    if not session or session.status != "completed":
        raise HTTPException(status_code=400, detail="Session is not ready for finalization")
    
    return APIResponse(data={"status": "completed"}, message="Session finalized. Report is being generated.")
