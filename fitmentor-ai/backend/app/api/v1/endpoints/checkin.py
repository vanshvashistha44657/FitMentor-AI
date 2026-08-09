from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.fitness import ProgressEntry
from app.models.user import User
from app.repositories.checkin_repository import CheckInRepository
from app.schemas.checkin import DailyCheckInOut, DailyCheckInRequest
from app.services.gamification_service import GamificationService

router = APIRouter(prefix="/checkins", tags=["Daily Check-in"])


@router.post("/today", response_model=DailyCheckInOut)
async def submit_daily_checkin(
    data: DailyCheckInRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Records the morning check-in, awards XP/streak credit, and — if a
    weight was reported — logs a progress entry so the weight trend chart
    stays in sync without a separate manual step.
    """
    checkin = await CheckInRepository(db).upsert_today(current_user.id, data.model_dump(exclude_unset=True))

    if data.weight_kg is not None:
        db.add(ProgressEntry(user_id=current_user.id, weight_kg=data.weight_kg))
        await db.commit()

    await GamificationService(db).award_checkin_and_update_streak(current_user.id)
    return checkin


@router.get("/history", response_model=list[DailyCheckInOut])
async def get_checkin_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CheckInRepository(db).get_range(current_user.id, days)
