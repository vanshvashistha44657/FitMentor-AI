import uuid

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fitness import NutritionPlan


class NutritionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def deactivate_all(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(NutritionPlan).where(NutritionPlan.user_id == user_id).values(is_active=False)
        )
        await self.db.commit()

    async def create(self, plan: NutritionPlan) -> NutritionPlan:
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_active(self, user_id: uuid.UUID) -> NutritionPlan | None:
        result = await self.db.execute(
            select(NutritionPlan)
            .where(NutritionPlan.user_id == user_id, NutritionPlan.is_active.is_(True))
            .order_by(desc(NutritionPlan.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self, user_id: uuid.UUID, limit: int = 20) -> list[NutritionPlan]:
        result = await self.db.execute(
            select(NutritionPlan)
            .where(NutritionPlan.user_id == user_id)
            .order_by(desc(NutritionPlan.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
