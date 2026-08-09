import uuid
from datetime import datetime

from pydantic import BaseModel


class NutritionPlanOut(BaseModel):
    id: uuid.UUID
    daily_calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int
    water_liters: float
    meal_plan: dict
    grocery_list: dict | None
    ai_rationale: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
