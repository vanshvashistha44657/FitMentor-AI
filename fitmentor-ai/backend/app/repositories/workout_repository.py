import uuid

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fitness import WorkoutPlan, WorkoutSession


class WorkoutRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def deactivate_all_plans(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(WorkoutPlan).where(WorkoutPlan.user_id == user_id).values(is_active=False)
        )
        await self.db.commit()

    async def create_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_active_plan(self, user_id: uuid.UUID) -> WorkoutPlan | None:
        result = await self.db.execute(
            select(WorkoutPlan)
            .where(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active.is_(True))
            .order_by(desc(WorkoutPlan.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_plan_history(self, user_id: uuid.UUID, limit: int = 20) -> list[WorkoutPlan]:
        result = await self.db.execute(
            select(WorkoutPlan)
            .where(WorkoutPlan.user_id == user_id)
            .order_by(desc(WorkoutPlan.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def log_session(self, session: WorkoutSession) -> WorkoutSession:
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_sessions(self, user_id: uuid.UUID, limit: int = 50) -> list[WorkoutSession]:
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .order_by(desc(WorkoutSession.performed_at))
            .limit(limit)
        )
        return list(result.scalars().all())
