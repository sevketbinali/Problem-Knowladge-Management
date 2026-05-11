import uuid
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy import text

from src.infrastructure.database import AsyncSessionLocal
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.models import User, Session, ProblemRecord, AuditLog

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="module")
async def test_user():
    """Create a test user for all repository tests."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        user = await repo.create_user(
            email=f"repo_test_{uuid.uuid4()}@example.com",
            hashed_password="hashed",
            full_name="Repo Test User"
        )
        yield user
        
        # Cleanup
        await session.execute(text("DELETE FROM audit_logs WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM problem_records WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM sessions WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user.id})
        await session.commit()

@settings(max_examples=5, deadline=None)
@given(
    email=st.emails(),
    full_name=st.text(min_size=1, max_size=100)
)
async def test_user_crud(email, full_name):
    """Test user creation and retrieval."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # Create
        user = await repo.create_user(
            email=f"test_{uuid.uuid4()}_{email}",
            hashed_password="hashed",
            full_name=full_name
        )
        assert user.id is not None
        assert user.email.endswith(email)
        
        # Get by email
        fetched = await repo.get_user_by_email(user.email)
        assert fetched is not None
        assert fetched.id == user.id
        
        # Cleanup
        await session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})
        await session.commit()

@settings(max_examples=5, deadline=None)
@given(
    problem_desc=st.text(min_size=20, max_size=200),
    methodology=st.sampled_from(["ishikawa", "5_why", "8d"])
)
async def test_session_crud(test_user, problem_desc, methodology):
    """Test session creation, retrieval, and update."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # Create
        db_session = await repo.create_session(
            user_id=test_user.id,
            problem_description=problem_desc,
            methodology=methodology
        )
        assert db_session.id is not None
        assert db_session.user_id == test_user.id
        
        # Get
        fetched = await repo.get_session(db_session.id)
        assert fetched is not None
        assert fetched.id == db_session.id
        
        # Update
        updated = await repo.update_session(db_session.id, status="completed")
        assert updated.status == "completed"
        
        # Cleanup
        await session.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": db_session.id})
        await session.commit()

@settings(max_examples=5, deadline=None)
@given(
    title=st.text(min_size=1, max_size=100),
    problem_desc=st.text(min_size=20, max_size=200)
)
async def test_record_crud(test_user, title, problem_desc):
    """Test problem record creation, retrieval, update, delete, and list."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # Need a session for foreign key
        db_session = await repo.create_session(
            user_id=test_user.id,
            problem_description=problem_desc,
            methodology="5_why"
        )
        
        # Create
        record = await repo.create_record(
            session_id=db_session.id,
            user_id=test_user.id,
            title=title,
            problem_description=problem_desc,
            methodology="5_why",
            step_responses={},
            root_cause="Unknown",
            corrective_actions=[],
            lessons_learned="None",
            resolution_status="open"
        )
        assert record.id is not None
        
        # Get
        fetched = await repo.get_record(record.id)
        assert fetched is not None
        assert fetched.title == title
        
        # Update
        updated = await repo.update_record(record.id, resolution_status="closed")
        assert updated.resolution_status == "closed"
        
        # List
        records = await repo.list_records(limit=10)
        assert len(records) >= 1
        assert any(r.id == record.id for r in records)
        
        # Delete
        success = await repo.delete_record(record.id)
        assert success is True
        assert await repo.get_record(record.id) is None
        
        # Cleanup session
        await session.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": db_session.id})
        await session.commit()
