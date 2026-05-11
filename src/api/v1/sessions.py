"""Session router for problem-solving flows."""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.dependencies import get_current_active_user, get_repository
from src.api.v1.schemas import SessionResponse, SessionStart, StepResponse
from src.domain.methodologies import MethodologyEngine
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.llm_service import LLMService
from src.infrastructure.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Problem Sessions"])


def get_session_service(
    repo: PostgreSQLRepository = Depends(get_repository)
) -> SessionService:
    return SessionService(repo, MethodologyEngine(), LLMService())


@router.post("/start", response_model=SessionResponse)
async def start_session(
    data: SessionStart,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    try:
        return await service.start_session(
            user_id=current_user.id,
            problem_description=data.problem_description,
            methodology=data.methodology
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/submit", response_model=SessionResponse)
async def submit_step(
    session_id: uuid.UUID,
    data: StepResponse,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    try:
        return await service.submit_step_response(session_id, data.response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/back", response_model=SessionResponse)
async def step_back(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    try:
        return await service.step_back(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/clarify")
async def clarify_problem(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    try:
        question = await service.get_clarification_question(session_id)
        return {"question": question}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
