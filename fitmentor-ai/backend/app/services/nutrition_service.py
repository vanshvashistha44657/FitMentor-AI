import uuid

from fastapi import HTTPException, status

from app.ai.nutrition_generator import (
    NUTRITION_SYSTEM_PROMPT,
    NutritionPlanAIResponse,
    build_nutrition_user_prompt,
)
from app.ai.provider import AIProviderError, generate_json
from app.models.fitness import NutritionPlan
from app.models.user import UserProfile
from app.repositories.nutrition_repository import NutritionRepository


class NutritionService:
    def __init__(self, repo: NutritionRepository):
        self.repo = repo

    async def generate_plan(self, user_id: uuid.UUID, profile: UserProfile) -> NutritionPlan:
        user_prompt = build_nutrition_user_prompt(profile)

        try:
            raw = await generate_json(NUTRITION_SYSTEM_PROMPT, user_prompt)
            validated = NutritionPlanAIResponse.model_validate(raw)
        except AIProviderError as e:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                f"The AI nutrition coach is temporarily unavailable: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                f"The AI nutrition coach returned an unexpected response: {e}",
            )

        await self.repo.deactivate_all(user_id)

        plan = NutritionPlan(
            user_id=user_id,
            daily_calories=validated.daily_calories,
            protein_g=validated.protein_g,
            carbs_g=validated.carbs_g,
            fat_g=validated.fat_g,
            fiber_g=validated.fiber_g,
            water_liters=validated.water_liters,
            meal_plan={
                "meals": {k: [i.model_dump() for i in v] for k, v in validated.meals.items()},
                "supplements": validated.supplements,
            },
            grocery_list=validated.grocery_list,
            ai_rationale=validated.rationale,
            is_active=True,
        )
        return await self.repo.create(plan)
