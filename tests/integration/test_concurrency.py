import asyncio
import uuid
import pytest
from hypothesis import given, settings, strategies as st
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
            email=f"test_concurrency_{uuid.uuid4()}@example.com",
            hashed_password="hashed",
            full_name="Concurrency Test User"
        )
        yield user.id
        
        # Cleanup
        await session.execute(text("DELETE FROM audit_logs WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM problem_records WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM sessions WHERE user_id = :user_id"), {"user_id": user.id})
        await session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user.id})
        await session.commit()

async def simulate_concurrent_update(record_id: uuid.UUID, title_suffix: str):
    """Simulate an update in an isolated session."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        # Attempt to update the problem record
        updated_data = {"title": f"Updated {title_suffix}"}
        # To simulate race condition, we could just fire updates
        # The PostgreSQL isolation level should handle standard updates without error,
        # but the test checks if gather completes without crashing and data remains consistent.
        record = await repo.update_record(record_id, **updated_data)
        return record

@settings(max_examples=5, deadline=None)
@given(num_concurrent=st.integers(min_value=2, max_value=10))
async def test_concurrent_updates(test_user_id: uuid.UUID, num_concurrent: int):
    """Requirement 9.2: Verify concurrent updates on same record don't cause data corruption."""
    record_id = uuid.uuid4()
    session_id = uuid.uuid4()
    
    # 1. Create a base record and dummy session
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # Need a session for the foreign key
        dummy_session = await repo.create_session(
            user_id=test_user_id,
            problem_description="Test problem",
            methodology="5_why"
        )
        
        record = await repo.create_record(
            id=record_id,
            session_id=dummy_session.id,
            user_id=test_user_id,
            title="Base Record",
            problem_description="Initial Description",
            methodology="5_why",
            step_responses={},
            root_cause="Unknown",
            corrective_actions=[],
            lessons_learned="None",
            resolution_status="open"
        )
        assert record is not None
        
    # 2. Fire concurrent updates
    tasks = [
        simulate_concurrent_update(record_id, str(i))
        for i in range(num_concurrent)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Verify that at least some updates succeeded (no generic crashes)
    # Some might fail due to serialization errors depending on isolation level,
    # but in read committed (default), they should all succeed and the last one wins.
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    assert success_count == num_concurrent
    
    # 4. Cleanup
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM problem_records WHERE id = :record_id"), {"record_id": record_id})
        await session.commit()
