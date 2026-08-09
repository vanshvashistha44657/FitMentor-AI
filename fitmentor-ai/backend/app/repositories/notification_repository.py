import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_for_user(self, user_id: uuid.UUID, limit: int = 50) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_due(self, before: datetime) -> list[Notification]:
        result = await self.db.execute(
            select(Notification).where(
                Notification.sent.is_(False), Notification.scheduled_for <= before
            )
        )
        return list(result.scalars().all())

    async def mark_read(self, notification_id: uuid.UUID) -> None:
        result = await self.db.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalar_one_or_none()
        if notification:
            notification.read = True
            await self.db.commit()

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        result = await self.db.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalar_one_or_none()
        if notification:
            notification.sent = True
            await self.db.commit()
