import uuid
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.models import User
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository

pytestmark = pytest.mark.asyncio

from src.core.config import settings as app_settings

@pytest.fixture(scope="module")
async def test_user_id():
    """Create a single test user to satisfy foreign key constraints."""
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()


        user_created = False
        repo = PostgreSQLRepository(session)
        try:
            user = await repo.create_user(
                email=f"test_{user_id}@example.com",
                hashed_password="hashed",
                full_name="Test User"
            )
            user_created = True
            yield user.id
        finally:
            if user_created:
                # Cleanup user after all tests in module
                await session.execute(text("DELETE FROM audit_logs WHERE user_id = :uid"), {"uid": user.id})
                await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user.id})
                await session.commit()


@settings(max_examples=20, deadline=None)
@given(
    operation=st.sampled_from(["create", "update", "delete"]),
    entity_type=st.sampled_from(["problem_record", "session"]),
    before_values=st.one_of(st.none(), st.dictionaries(st.text(min_size=1).filter(lambda s: "\x00" not in s), st.text(min_size=1).filter(lambda s: "\x00" not in s), max_size=3)),
    after_values=st.one_of(st.none(), st.dictionaries(st.text(min_size=1).filter(lambda s: "\x00" not in s), st.text(min_size=1).filter(lambda s: "\x00" not in s), max_size=3))
)
async def test_audit_log_integrity(test_user_id: uuid.UUID, operation: str, entity_type: str, before_values: dict | None, after_values: dict | None):

    """Requirement 9.5: Verify audit log entries correctly store and retrieve all data points."""
    entity_id = uuid.uuid4()
    
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # 1. Create the audit log
        log = await repo.create_audit_log(
            user_id=test_user_id,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            before_values=before_values,
            after_values=after_values
        )
        
        # Verify returned object
        assert log.id is not None
        assert log.user_id == test_user_id
        assert log.operation == operation
        assert log.entity_type == entity_type
        assert log.entity_id == entity_id
        assert log.before_values == before_values
        assert log.after_values == after_values
        assert log.created_at is not None
        
        log_id = log.id

    # 2. Retrieve it from DB to ensure it was properly persisted
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from src.infrastructure.models import AuditLog
        
        result = await session.execute(select(AuditLog).where(AuditLog.id == log_id))
        persisted_log = result.scalar_one_or_none()
        
        assert persisted_log is not None
        assert persisted_log.user_id == test_user_id
        assert persisted_log.operation == operation
        assert persisted_log.entity_type == entity_type
        assert persisted_log.entity_id == entity_id
        assert persisted_log.before_values == before_values
        assert persisted_log.after_values == after_values
