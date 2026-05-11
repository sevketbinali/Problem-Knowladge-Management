import uuid
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy import text

from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.models import User, Session, ProblemRecord, AuditLog

pytestmark = pytest.mark.asyncio



@settings(max_examples=10, deadline=None)
@given(
    email=st.emails().filter(lambda s: "\x00" not in s),
    full_name=st.text(min_size=1, max_size=100).filter(lambda s: "\x00" not in s),
    problem_desc=st.text(min_size=20, max_size=200).filter(lambda s: "\x00" not in s),
    methodology=st.sampled_from(["ishikawa", "5_why", "8d"]),
    title=st.text(min_size=1, max_size=100).filter(lambda s: "\x00" not in s)
)
async def test_repository_lifecycle(email, full_name, problem_desc, methodology, title):

    """Test the full lifecycle of users, sessions, and records in a single test to avoid loop issues."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # 1. User Test
        unique_email = f"test_{uuid.uuid4()}_{email}"
        user = await repo.create_user(
            email=unique_email,
            hashed_password="hashed",
            full_name=full_name
        )
        assert user.id is not None
        
        fetched_user = await repo.get_user_by_email(unique_email)
        assert fetched_user.id == user.id
        
        # 2. Session Test
        db_session = await repo.create_session(
            user_id=user.id,
            problem_description=problem_desc,
            methodology=methodology
        )
        assert db_session.id is not None
        
        fetched_session = await repo.get_session(db_session.id)
        assert fetched_session.id == db_session.id
        
        # 3. Record Test
        record = await repo.create_record(
            session_id=db_session.id,
            user_id=user.id,
            title=title,
            problem_description=problem_desc,
            methodology=methodology,
            step_responses={},
            root_cause="Unknown",
            corrective_actions=[],
            lessons_learned="None",
            resolution_status="open"
        )
        assert record.id is not None
        
        updated_record = await repo.update_record(record.id, resolution_status="closed")
        assert updated_record.resolution_status == "closed"
        
        # 4. Cleanup
        await session.execute(text("DELETE FROM problem_records WHERE id = :id"), {"id": record.id})
        await session.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": db_session.id})
        await session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})
        await session.commit()

