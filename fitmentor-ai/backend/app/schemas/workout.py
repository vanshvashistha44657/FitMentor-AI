import uuid
from datetime import datetime

from pydantic import BaseModel


class GenerateWorkoutRequest(BaseModel):
    week_number: int = 1
    is_deload_week: bool = False


class WorkoutPlanOut(BaseModel):
    id: uuid.UUID
    split_type: str
    goal: str
    week_number: int
    is_deload_week: bool
    is_active: bool
    plan_data: dict
    ai_rationale: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LogSetEntry(BaseModel):
    exercise: str
    weight_kg: float | None = None
    reps: int | None = None
    rpe: float | None = None
    notes: str | None = None


class LogWorkoutSessionRequest(BaseModel):
    plan_id: uuid.UUID | None = None
    day_label: str
    duration_minutes: int | None = None
    completed: bool = True
    sets: list[LogSetEntry]


class WorkoutSessionOut(BaseModel):
    id: uuid.UUID
    day_label: str
    performed_at: datetime
    duration_minutes: int | None
    total_volume_kg: float | None
    avg_rpe: float | None
    completed: bool
    log_data: dict

    model_config = {"from_attributes": True}
