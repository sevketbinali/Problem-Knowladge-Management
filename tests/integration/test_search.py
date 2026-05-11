"""Integration tests for record search functionality.

Validates: Requirements 8.1, 8.2, 8.7 (Özellik 19)
"""
import uuid
import pytest
import asyncio
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
            email=f"search_test_{uuid.uuid4()}@example.com",
            hashed_password="hashed",
            full_name="Search Test User"
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
            problem_description="Test search session description.",
            methodology="5_why"
        )
        yield db_session.id

@settings(max_examples=5, deadline=None)
@given(query=st.text(min_size=10, max_size=50).filter(lambda s: "\x00" not in s))
async def test_search_ordering_and_limit(test_user_id: uuid.UUID, test_session_id: uuid.UUID, query: str):
    """Requirement 8.1, 8.2, 8.7: Verify search results are ordered by date and limited to 10."""
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        
        # 1. Create multiple records, some matching the query
        # We create 15 records to test the limit of 10
        record_ids = []
        for i in range(15):
            # Alternate between matching and not matching
            title = f"{query} Match {i}" if i % 2 == 0 else f"No Match {i}"
            record = await repo.create_record(
                session_id=test_session_id,
                user_id=test_user_id,
                title=title,
                problem_description="Description for search test.",
                methodology="5_why",
                step_responses={},
                root_cause="Unknown",
                corrective_actions=[],
                lessons_learned="None",
                resolution_status="open"
            )
            record_ids.append(record.id)
            await asyncio.sleep(0.01) # Ensure different created_at
        
        # 2. Perform search
        results = await repo.search_records(query, limit=10)
        
        # 3. Verify results
        assert len(results) <= 10
        # Check ordering (should be descending)
        for i in range(len(results) - 1):
            assert results[i].created_at >= results[i+1].created_at
        
        # Verify they actually match
        for r in results:
            assert query.lower() in r.title.lower() or query.lower() in r.problem_description.lower()

        # 4. Cleanup records
        for rid in record_ids:
            await session.execute(text("DELETE FROM problem_records WHERE id = :rid"), {"rid": rid})
        await session.commit()
