"""Property-based tests for authentication and security.

Validates: Requirements 10.1, 10.3, 10.5, 10.7
"""
import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError

from src.core.auth import get_password_hash, verify_password, create_access_token, decode_access_token


@settings(deadline=None, max_examples=10)
@given(st.text(min_size=8, max_size=100))
def test_password_hashing_security(password: str) -> None:
    """Property 26: Password hashing security.
    - Stored hash must be bcrypt format.
    - Plain text must never be stored (verified by hashing and checking).
    
    Validates: Requirement 10.5
    """
    hashed = get_password_hash(password)
    
    # Bcrypt hashes start with $2b$ or $2a$ and are exactly 60 characters
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60
    assert hashed != password  # Plain text is not stored
    
    # Verification must work
    assert verify_password(password, hashed) is True
    # Wrong password must fail
    assert verify_password(password + "wrong", hashed) is False


@given(st.dictionaries(
    keys=st.text(min_size=1, max_size=20),
    values=st.text(min_size=1, max_size=100),
    min_size=1,
    max_size=5
))
def test_token_roundtrip(payload: dict) -> None:
    """Tests that JWT tokens can be created and decoded correctly."""
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    
    assert decoded is not None
    # Check that original payload keys are present (exp will be added)
    for key, value in payload.items():
        assert decoded[key] == value
    assert "exp" in decoded


def test_invalid_token() -> None:
    """Tests that invalid tokens return None."""
    assert decode_access_token("invalid.token.here") is None
    assert decode_access_token("") is None
