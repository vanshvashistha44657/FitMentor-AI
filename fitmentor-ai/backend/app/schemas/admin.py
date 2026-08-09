import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminUserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    is_onboarded: bool
    subscription_tier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsSummaryOut(BaseModel):
    total_users: int
    onboarded_users: int
    onboarding_rate_percent: float
    total_workout_plans: int
    total_workout_sessions: int
    total_nutrition_plans: int
    total_chat_messages: int
    subscription_tier_breakdown: dict[str, int]


class ExerciseCreateRequest(BaseModel):
    name: str
    category: str
    primary_muscle: str
    secondary_muscles: str | None = None
    equipment_needed: str | None = None
    difficulty: str
    instructions: str | None = None
    video_url: str | None = None


class ExerciseOut(ExerciseCreateRequest):
    id: uuid.UUID

    model_config = {"from_attributes": True}
