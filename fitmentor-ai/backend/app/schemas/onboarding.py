import uuid

from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    # Basic details
    age: int = Field(ge=13, le=100)
    gender: str
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    target_weight_kg: float = Field(gt=0)
    body_fat_percent: float | None = None

    # Goal & experience
    fitness_goal: str  # lose_fat | build_muscle | recomposition | weight_gain | athletic_performance | powerlifting | bodybuilding | general_fitness
    fitness_level: str  # beginner | intermediate | advanced
    experience: str     # never | <1y | 1-3y | 3-5y | 5y+

    # Health
    medical_conditions: str | None = None
    past_injuries: str | None = None
    medications: str | None = None
    allergies: str | None = None

    # Diet
    diet_type: str  # vegetarian | vegan | non_vegetarian | eggetarian
    food_allergies: str | None = None
    preferred_cuisine: str | None = None
    daily_budget: float | None = None

    # Training logistics
    workout_location: str  # home | gym | hybrid
    gym_equipment: str | None = None
    workout_time: str | None = None
    workout_days: int = Field(ge=1, le=7)
    workout_duration_minutes: int = Field(ge=10, le=240)

    # Lifestyle
    sleep_time: str | None = None
    wake_time: str | None = None
    stress_level: str | None = None
    water_intake_liters: float | None = None
    occupation: str | None = None
    activity_level: str  # sedentary | lightly_active | moderately_active | very_active | extremely_active
    smoking: bool = False
    alcohol: bool = False
    daily_step_count: int | None = None

    # Preferences
    favorite_exercises: str | None = None
    disliked_exercises: str | None = None
    target_muscles: str | None = None
    weak_muscles: str | None = None
    strong_muscles: str | None = None


class UserProfileOut(OnboardingRequest):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class AIScoreOut(BaseModel):
    fitness_score: float
    health_score: float
    muscle_balance_score: float
    lifestyle_score: float
    recovery_score: float
    explanations: dict[str, str]

    model_config = {"from_attributes": True}
