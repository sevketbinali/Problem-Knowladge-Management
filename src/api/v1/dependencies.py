"""FastAPI dependencies for database sessions and authentication."""
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import decode_access_token
from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.redis_service import RedisService

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_repository(db: AsyncSession = Depends(get_db)) -> PostgreSQLRepository:
    """Dependency to provide a PostgreSQL repository."""
    return PostgreSQLRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: PostgreSQLRepository = Depends(get_repository)
) -> User:
    """Dependency to validate JWT and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = await repo.get_user_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    # For now, all users are active
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to ensure the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user


async def get_redis() -> AsyncGenerator[RedisService, None]:
    """Dependency to provide a Redis service."""
    service = RedisService()
    try:
        yield service
    finally:
        await service.close()


async def check_rate_limit(
    current_user: User = Depends(get_current_active_user),
    redis_service: RedisService = Depends(get_redis)
):
    """Dependency to enforce rate limiting per user."""
    allowed = await redis_service.check_rate_limit(str(current_user.id))
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
