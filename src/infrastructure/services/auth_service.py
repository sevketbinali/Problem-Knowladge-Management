"""High-level authentication service for user login and token management."""
from datetime import timedelta
from typing import Optional

from src.core.auth import create_access_token, get_password_hash, verify_password
from src.core.config import settings
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository


class AuthService:
    def __init__(self, repository: PostgreSQLRepository):
        self.repository = repository

    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user and return user data if successful."""
        user = await self.repository.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }

    async def login_for_access_token(self, email: str, password: str) -> Optional[dict]:
        """Verify user and generate access token."""
        user_data = await self.authenticate_user(email, password)
        if not user_data:
            return None
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data["email"], "role": user_data["role"], "user_id": user_data["id"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }

    async def register_user(self, email: str, password: str, full_name: str, role: str = "user") -> dict:
        """Register a new user."""
        hashed_password = get_password_hash(password)
        user = await self.repository.create_user(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
