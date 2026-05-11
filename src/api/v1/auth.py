"""Authentication router for login and registration."""
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.dependencies import get_repository
from src.api.v1.schemas import Token, UserCreate, UserLogin
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    repo: PostgreSQLRepository = Depends(get_repository)
):
    auth_service = AuthService(repo)
    existing_user = await repo.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_PASSWORD, # Requirement 10.3 mentions specific error codes
            detail="User already exists"
        )
    return await auth_service.register_user(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    repo: PostgreSQLRepository = Depends(get_repository)
):
    auth_service = AuthService(repo)
    token_data = await auth_service.login_for_access_token(
        email=user_in.email,
        password=user_in.password
    )
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data
