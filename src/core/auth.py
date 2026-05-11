"""Authentication utilities for hashing passwords and managing JWT tokens."""
import bcrypt
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from src.core.config import settings


def _prepare_password(password: str) -> bytes:
    """Hash password with SHA256 and base64 encode to avoid bcrypt 72-byte limit."""
    # We use SHA256 to ensure the input to bcrypt is always a fixed-length string (well, base64 of 256 bits).
    # This bypasses the 72-byte limit of bcrypt while maintaining security.
    sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.b64encode(sha256_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed one."""
    return bcrypt.checkpw(
        _prepare_password(plain_password), 
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for a plain password."""
    # Requirement 10.5: Bcrypt with at least 12 cost factor
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(_prepare_password(password), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
