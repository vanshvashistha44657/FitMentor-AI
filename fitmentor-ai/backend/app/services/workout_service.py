import uuid

from fastapi import HTTPException, status

from app.ai.provider import AIProviderError, generate_json
from app.ai.workout_generator import (
    WORKOUT_SYSTEM_PROMPT,
    WorkoutPlanAIResponse,
    build_workout_user_prompt,
)
from app.models.fitness import WorkoutPlan
from app.models.user import UserProfile
from app.repositories.workout_repository import WorkoutRepository


class WorkoutService:
    def __init__(self, repo: WorkoutRepository):
        self.repo = repo

    async def generate_plan(
        self, user_id: uuid.UUID, profile: UserProfile, week_number: int = 1, is_deload_week: bool = False
    ) -> WorkoutPlan:
        user_prompt = build_workout_user_prompt(profile, week_number, is_deload_week)

        try:
            raw = await generate_json(WORKOUT_SYSTEM_PROMPT, user_prompt)
            validated = WorkoutPlanAIResponse.model_validate(raw)
        except AIProviderError as e:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                f"The AI coach is temporarily unavailable and couldn't generate your plan: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                f"The AI coach returned an unexpected response and the plan couldn't be validated: {e}",
            )

        # Only one active plan at a time — new generation supersedes the old.
        await self.repo.deactivate_all_plans(user_id)

        plan = WorkoutPlan(
            user_id=user_id,
            split_type=validated.split_type,
            goal=profile.fitness_goal,
            week_number=validated.week_number,
            is_deload_week=validated.is_deload_week,
            is_active=True,
            plan_data=validated.model_dump(),
            ai_rationale=validated.rationale,
        )
        return await self.repo.create_plan(plan)
