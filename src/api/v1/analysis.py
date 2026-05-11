"""Analysis router for generating reports."""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.dependencies import get_current_active_user, get_repository
from src.api.v1.schemas import AnalysisReport
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.analysis_service import AnalysisService
from src.infrastructure.services.llm_service import LLMService

router = APIRouter(prefix="/analysis", tags=["Analysis"])


def get_analysis_service(
    repo: PostgreSQLRepository = Depends(get_repository)
) -> AnalysisService:
    return AnalysisService(repo, LLMService())


@router.post("/{session_id}/report", response_model=AnalysisReport)
async def generate_report(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: AnalysisService = Depends(get_analysis_service)
):
    try:
        return await service.generate_final_report(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
