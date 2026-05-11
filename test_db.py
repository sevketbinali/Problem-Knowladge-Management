import asyncio
from sqlalchemy import text
from src.infrastructure.database import AsyncSessionLocal

async def main():
    import uuid
    from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        user = await repo.create_user(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="hashed",
            full_name="Test User"
        )
        print(f"Created user: {user.id}")


if __name__ == "__main__":
    asyncio.run(main())
