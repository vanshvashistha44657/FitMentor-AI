from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.nutrition_repository import NutritionRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.nutrition import NutritionPlanOut
from app.services.nutrition_service import NutritionService

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.post("/generate", response_model=NutritionPlanOut)
async def generate_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await ProfileRepository(db).get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(404, "Complete onboarding before generating a nutrition plan")

    service = NutritionService(NutritionRepository(db))
    return await service.generate_plan(current_user.id, profile)


@router.get("/active", response_model=NutritionPlanOut)
async def get_active_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await NutritionRepository(db).get_active(current_user.id)
    if not plan:
        raise HTTPException(404, "No active nutrition plan — generate one first")
    return plan


@router.get("/history", response_model=list[NutritionPlanOut])
async def get_nutrition_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await NutritionRepository(db).get_history(current_user.id)
