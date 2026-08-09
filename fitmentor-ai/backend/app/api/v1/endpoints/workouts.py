from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.fitness import WorkoutSession
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.workout import (
    GenerateWorkoutRequest,
    LogWorkoutSessionRequest,
    WorkoutPlanOut,
    WorkoutSessionOut,
)
from app.services.gamification_service import GamificationService
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post("/generate", response_model=WorkoutPlanOut)
async def generate_workout_plan(
    data: GenerateWorkoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await ProfileRepository(db).get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(404, "Complete onboarding before generating a workout plan")

    service = WorkoutService(WorkoutRepository(db))
    plan = await service.generate_plan(current_user.id, profile, data.week_number, data.is_deload_week)
    return plan


@router.get("/active", response_model=WorkoutPlanOut)
async def get_active_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await WorkoutRepository(db).get_active_plan(current_user.id)
    if not plan:
        raise HTTPException(404, "No active workout plan — generate one first")
    return plan


@router.get("/history", response_model=list[WorkoutPlanOut])
async def get_plan_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutRepository(db).get_plan_history(current_user.id)


@router.post("/sessions", response_model=WorkoutSessionOut, status_code=201)
async def log_workout_session(
    data: LogWorkoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logs a completed workout, computes total volume/avg RPE, and awards
    gamification XP for consistency."""
    valid_sets = [s for s in data.sets if s.weight_kg and s.reps]
    total_volume = sum((s.weight_kg or 0) * (s.reps or 0) for s in valid_sets)
    rpes = [s.rpe for s in data.sets if s.rpe is not None]
    avg_rpe = round(sum(rpes) / len(rpes), 1) if rpes else None

    session = WorkoutSession(
        user_id=current_user.id,
        plan_id=data.plan_id,
        day_label=data.day_label,
        duration_minutes=data.duration_minutes,
        total_volume_kg=total_volume or None,
        avg_rpe=avg_rpe,
        completed=data.completed,
        log_data={"sets": [s.model_dump() for s in data.sets]},
    )
    saved = await WorkoutRepository(db).log_session(session)

    if data.completed:
        await GamificationService(db).award_workout_completion(current_user.id)

    return saved


@router.get("/sessions", response_model=list[WorkoutSessionOut])
async def get_workout_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutRepository(db).get_sessions(current_user.id)
