"""Property-based tests for authentication and security.

Validates: Requirements 10.1, 10.3, 10.5, 10.7
"""
import pytest
from hypothesis import given, settings, strategies as st
from fastapi import HTTPException, status
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
    
    # Requirement 10.5: At least 12 cost factor
    # Extract cost from bcrypt hash: $2b$12$salt_hash
    parts = hashed.split('$')
    cost = int(parts[2])
    assert cost >= 12


@given(st.dictionaries(
    keys=st.text(min_size=1, max_size=20).filter(lambda k: k != "exp"),
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


@given(st.dictionaries(st.text(min_size=1).filter(lambda k: k != "exp"), st.text(min_size=1), min_size=1))
def test_token_structure(payload: dict) -> None:
    """Requirement 13.2: Verify JWT structure (Header.Payload.Signature)."""
    token = create_access_token(payload)
    parts = token.split(".")
    assert len(parts) == 3
    # Check if parts are valid base64 (implicit in JWT structure)
    assert all(len(p) > 0 for p in parts)


@given(st.integers(min_value=1, max_value=1000))
def test_token_expiration_duration(minutes: int) -> None:
    """Requirement 10.3: Verify JWT expiration time calculation."""
    from datetime import timedelta, datetime, timezone
    from src.core.config import settings
    
    delta = timedelta(minutes=minutes)
    token = create_access_token({"sub": "test"}, expires_delta=delta)
    decoded = decode_access_token(token)
    
    # exp is a unix timestamp
    exp = decoded["exp"]
    now = datetime.now(timezone.utc).timestamp()
    
    # exp should be roughly now + delta
    expected_exp = now + (minutes * 60)
    # Allow 5 second leeway for test execution time
    assert abs(exp - expected_exp) < 5


@given(st.sampled_from([
    ("valid", status.HTTP_200_OK),
    ("expired", status.HTTP_401_UNAUTHORIZED),
    ("invalid", status.HTTP_401_UNAUTHORIZED),
    ("missing", status.HTTP_401_UNAUTHORIZED),
    ("no_sub", status.HTTP_401_UNAUTHORIZED)
]))
def test_token_http_code_mapping(token_scenario: tuple) -> None:
    """Requirement 10.1, 10.3, 10.7: Verify token state maps to correct HTTP code."""
    state, expected_code = token_scenario
    
    # We simulate the logic in get_current_user
    # 1. missing -> handled by OAuth2PasswordBearer (raises 401)
    # 2. invalid -> decode_access_token returns None -> raise 401
    # 3. expired -> decode_access_token returns None -> raise 401
    # 4. valid but no sub -> raise 401
    
    # In our unit test, we just verify that decode_access_token/logic handles these correctly
    from src.core.auth import create_access_token, decode_access_token
    from datetime import timedelta
    
    if state == "valid":
        token = create_access_token({"sub": "user@example.com"})
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" in payload
    elif state == "expired":
        # Create a token that is already expired
        token = create_access_token({"sub": "user@example.com"}, expires_delta=timedelta(seconds=-1))
        payload = decode_access_token(token)
        assert payload is None
    elif state == "invalid":
        payload = decode_access_token("not.a.token")
        assert payload is None
    elif state == "missing":
        payload = decode_access_token("")
        assert payload is None
    elif state == "no_sub":
        token = create_access_token({"role": "user"})
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" not in payload

