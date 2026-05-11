"""Integration tests for ProblemRecord operations, specifically metadata handling.

Validates: Requirement 6.5 (Özellik 6)
"""
import uuid
import pytest
from hypothesis import given, strategies as st
from sqlalchemy import text

from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="module")
async def test_user_id():
    """Create a test user for foreign keys."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        user = await repo.create_user(
            email=f"records_test_{uuid.uuid4()}@example.com",
            hashed_password="hashed",
            full_name="Records Test User"
        )
        yield user.id
        
        # Cleanup
        await session.execute(text("DELETE FROM audit_logs WHERE user_id = :uid"), {"uid": user.id})
        await session.execute(text("DELETE FROM problem_records WHERE user_id = :uid"), {"uid": user.id})
        await session.execute(text("DELETE FROM sessions WHERE user_id = :uid"), {"uid": user.id})
        await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user.id})
        await session.commit()

@pytest.fixture(scope="module")
async def test_session_id(test_user_id: uuid.UUID):
    """Create a test session for foreign keys."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        db_session = await repo.create_session(
            user_id=test_user_id,
            problem_description="Test problem description with enough length to pass validation.",
            methodology="5_why"
        )
        yield db_session.id

@given(metadata=st.one_of(st.none(), st.dictionaries(st.text().filter(lambda s: "\x00" not in s), st.text().filter(lambda s: "\x00" not in s))))
async def test_metadata_null_assignment(test_user_id: uuid.UUID, test_session_id: uuid.UUID, metadata: dict | None):
    """Requirement 6.5: Verify metadata field accepts null or empty dict."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        record_id = uuid.uuid4()
        record = await repo.create_record(
            id=record_id,
            session_id=test_session_id,
            user_id=test_user_id,
            title="Metadata Test",
            problem_description="Test problem description with enough length to pass validation.",
            methodology="5_why",
            step_responses={},
            root_cause="Unknown",
            corrective_actions=[],
            lessons_learned="None",
            resolution_status="open",
            meta_data=metadata
        )
        
        assert record is not None
        assert record.meta_data == metadata
        
        # Cleanup record
        await session.execute(text("DELETE FROM problem_records WHERE id = :rid"), {"rid": record_id})
        await session.commit()
