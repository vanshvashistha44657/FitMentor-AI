import uuid
from datetime import date

from pydantic import BaseModel, Field


class DailyCheckInRequest(BaseModel):
    weight_kg: float | None = None
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    energy_level: int | None = Field(default=None, ge=1, le=10)
    mood: int | None = Field(default=None, ge=1, le=10)
    soreness: int | None = Field(default=None, ge=1, le=10)
    stress: int | None = Field(default=None, ge=1, le=10)
    water_liters: float | None = None
    calories_yesterday: int | None = None
    workout_completed: bool | None = None
    steps: int | None = None


class DailyCheckInOut(DailyCheckInRequest):
    id: uuid.UUID
    checkin_date: date

    model_config = {"from_attributes": True}
