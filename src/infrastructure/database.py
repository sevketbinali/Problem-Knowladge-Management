from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=15,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Requirement 1.3: Initialize database and create initial admin user."""
    from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
    from src.infrastructure.services.auth_service import AuthService
    import src.infrastructure.models  # Import all models to register with Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        repo = PostgreSQLRepository(session)
        # Check if admin already exists
        admin_email = settings.INITIAL_ADMIN_EMAIL or "admin@pkm.local"
        existing_admin = await repo.get_user_by_email(admin_email)
        
        if not existing_admin:
            auth_service = AuthService(repo)
            admin_pass = settings.INITIAL_ADMIN_PASSWORD or "Admin123!"
            await auth_service.register_user(
                email=admin_email,
                password=admin_pass,
                full_name="System Administrator",
                role="admin"
            )
            print(f"Initial admin created: {admin_email}")
