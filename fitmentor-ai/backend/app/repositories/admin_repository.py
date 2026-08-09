import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import ChatMessage
from app.models.fitness import Exercise, NutritionPlan, WorkoutPlan, WorkoutSession
from app.models.user import User


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def set_user_active(self, user_id: uuid.UUID, is_active: bool) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = is_active
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def get_analytics_summary(self) -> dict:
        total_users = (await self.db.execute(select(func.count(User.id)))).scalar_one()
        onboarded_users = (await self.db.execute(select(func.count(User.id)).where(User.is_onboarded.is_(True)))).scalar_one()
        total_workout_plans = (await self.db.execute(select(func.count(WorkoutPlan.id)))).scalar_one()
        total_sessions = (await self.db.execute(select(func.count(WorkoutSession.id)))).scalar_one()
        total_nutrition_plans = (await self.db.execute(select(func.count(NutritionPlan.id)))).scalar_one()
        total_chat_messages = (await self.db.execute(select(func.count(ChatMessage.id)))).scalar_one()

        tier_counts_result = await self.db.execute(
            select(User.subscription_tier, func.count(User.id)).group_by(User.subscription_tier)
        )
        tier_counts = {tier.value: count for tier, count in tier_counts_result.all()}

        return {
            "total_users": total_users,
            "onboarded_users": onboarded_users,
            "onboarding_rate_percent": round(onboarded_users / total_users * 100, 1) if total_users else 0,
            "total_workout_plans": total_workout_plans,
            "total_workout_sessions": total_sessions,
            "total_nutrition_plans": total_nutrition_plans,
            "total_chat_messages": total_chat_messages,
            "subscription_tier_breakdown": tier_counts,
        }

    async def list_exercises(self, limit: int = 200) -> list[Exercise]:
        result = await self.db.execute(select(Exercise).order_by(Exercise.name).limit(limit))
        return list(result.scalars().all())

    async def create_exercise(self, exercise: Exercise) -> Exercise:
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def delete_exercise(self, exercise_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
        exercise = result.scalar_one_or_none()
        if exercise:
            await self.db.delete(exercise)
            await self.db.commit()
            return True
        return False
