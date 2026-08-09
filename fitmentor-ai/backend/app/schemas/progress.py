import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ProgressEntryRequest(BaseModel):
    weight_kg: float | None = None
    body_fat_percent: float | None = None
    measurements: dict | None = None  # {"chest_cm": 100, "waist_cm": 80, ...}
    photo_urls: dict | None = None    # {"front": "url", "side": "url", "back": "url"}


class ProgressEntryOut(ProgressEntryRequest):
    id: uuid.UUID
    entry_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class WeeklyReviewOut(BaseModel):
    weight_trend: dict
    adherence_percent: float
    workout_score: float
    avg_calories: int | None
    avg_sleep_hours: float | None
    recovery_score: float | None
    total_workout_volume_kg: float | None
    workouts_completed: int
    suggestions: list[str]
