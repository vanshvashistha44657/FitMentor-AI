import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fitness import AIScore
from app.models.user import UserProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, data: dict) -> UserProfile:
        existing = await self.get_by_user_id(user_id)
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            profile = existing
        else:
            profile = UserProfile(user_id=user_id, **data)
            self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile


class ScoreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, score: AIScore) -> AIScore:
        self.db.add(score)
        await self.db.commit()
        await self.db.refresh(score)
        return score

    async def get_latest(self, user_id: uuid.UUID) -> AIScore | None:
        result = await self.db.execute(
            select(AIScore).where(AIScore.user_id == user_id).order_by(desc(AIScore.created_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self, user_id: uuid.UUID, limit: int = 30) -> list[AIScore]:
        result = await self.db.execute(
            select(AIScore).where(AIScore.user_id == user_id).order_by(desc(AIScore.created_at)).limit(limit)
        )
        return list(result.scalars().all())
