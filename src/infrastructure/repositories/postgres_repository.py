import uuid
from typing import Any, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import AuditLog, ProblemRecord, Session, User


class PostgreSQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Session CRUD
    async def create_session(self, user_id: uuid.UUID, problem_description: str, methodology: str) -> Session:
        db_session = Session(
            user_id=user_id,
            problem_description=problem_description,
            methodology=methodology
        )
        self.session.add(db_session)
        await self.session.commit()
        await self.session.refresh(db_session)
        return db_session

    async def get_session(self, session_id: uuid.UUID) -> Session | None:
        result = await self.session.execute(select(Session).where(Session.id == session_id))
        return result.scalar_one_or_none()

    async def update_session(self, session_id: uuid.UUID, **kwargs) -> Session | None:
        await self.session.execute(
            update(Session).where(Session.id == session_id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_session(session_id)

    # ProblemRecord CRUD
    async def create_record(self, **kwargs) -> ProblemRecord:
        record = ProblemRecord(**kwargs)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_record(self, record_id: uuid.UUID) -> ProblemRecord | None:
        result = await self.session.execute(select(ProblemRecord).where(ProblemRecord.id == record_id))
        return result.scalar_one_or_none()

    async def update_record(self, record_id: uuid.UUID, **kwargs) -> ProblemRecord | None:
        await self.session.execute(
            update(ProblemRecord).where(ProblemRecord.id == record_id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_record(record_id)

    async def delete_record(self, record_id: uuid.UUID) -> bool:
        result = await self.session.execute(delete(ProblemRecord).where(ProblemRecord.id == record_id))
        await self.session.commit()
        return result.rowcount > 0

    async def list_records(self, skip: int = 0, limit: int = 20) -> Sequence[ProblemRecord]:
        result = await self.session.execute(select(ProblemRecord).offset(skip).limit(limit))
        return result.scalars().all()

    # Audit Logs
    async def create_audit_log(self, user_id: uuid.UUID, operation: str, entity_type: str, entity_id: uuid.UUID, 
                             before_values: dict[str, Any] | None = None, 
                             after_values: dict[str, Any] | None = None) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            before_values=before_values,
            after_values=after_values
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log
