import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fitness import ProgressEntry


class ProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, entry: ProgressEntry) -> ProgressEntry:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_range(self, user_id: uuid.UUID, days: int = 90) -> list[ProgressEntry]:
        since = date.today() - timedelta(days=days)
        result = await self.db.execute(
            select(ProgressEntry)
            .where(ProgressEntry.user_id == user_id, ProgressEntry.entry_date >= since)
            .order_by(ProgressEntry.entry_date.asc())
        )
        return list(result.scalars().all())
