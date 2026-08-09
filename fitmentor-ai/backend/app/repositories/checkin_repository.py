import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fitness import DailyCheckIn


class CheckInRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_today(self, user_id: uuid.UUID, data: dict) -> DailyCheckIn:
        today = date.today()
        result = await self.db.execute(
            select(DailyCheckIn).where(
                DailyCheckIn.user_id == user_id, DailyCheckIn.checkin_date == today
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            checkin = existing
        else:
            checkin = DailyCheckIn(user_id=user_id, checkin_date=today, **data)
            self.db.add(checkin)
        await self.db.commit()
        await self.db.refresh(checkin)
        return checkin

    async def get_range(self, user_id: uuid.UUID, days: int = 7) -> list[DailyCheckIn]:
        since = date.today() - timedelta(days=days)
        result = await self.db.execute(
            select(DailyCheckIn)
            .where(DailyCheckIn.user_id == user_id, DailyCheckIn.checkin_date >= since)
            .order_by(DailyCheckIn.checkin_date.asc())
        )
        return list(result.scalars().all())
