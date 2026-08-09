import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models.fitness import Exercise
from app.models.user import User
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import (
    AdminUserOut,
    AnalyticsSummaryOut,
    ExerciseCreateRequest,
    ExerciseOut,
)

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await AdminRepository(db).list_users(limit, offset)


@router.post("/users/{user_id}/deactivate", response_model=AdminUserOut)
async def deactivate_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await AdminRepository(db).set_user_active(user_id, False)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.post("/users/{user_id}/reactivate", response_model=AdminUserOut)
async def reactivate_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await AdminRepository(db).set_user_active(user_id, True)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.get("/analytics", response_model=AnalyticsSummaryOut)
async def get_analytics(db: AsyncSession = Depends(get_db)):
    return await AdminRepository(db).get_analytics_summary()


@router.get("/exercises", response_model=list[ExerciseOut])
async def list_exercises(db: AsyncSession = Depends(get_db)):
    return await AdminRepository(db).list_exercises()


@router.post("/exercises", response_model=ExerciseOut, status_code=201)
async def create_exercise(data: ExerciseCreateRequest, db: AsyncSession = Depends(get_db)):
    exercise = Exercise(**data.model_dump())
    return await AdminRepository(db).create_exercise(exercise)


@router.delete("/exercises/{exercise_id}", status_code=204)
async def delete_exercise(exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await AdminRepository(db).delete_exercise(exercise_id)
    if not deleted:
        raise HTTPException(404, "Exercise not found")
