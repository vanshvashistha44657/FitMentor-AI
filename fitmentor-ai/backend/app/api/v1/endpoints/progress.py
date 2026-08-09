from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.fitness import ProgressEntry
from app.models.user import User
from app.repositories.checkin_repository import CheckInRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.progress import ProgressEntryOut, ProgressEntryRequest, WeeklyReviewOut
from app.services.weekly_review_service import WeeklyReviewService

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


@router.post("/entries", response_model=ProgressEntryOut, status_code=201)
async def log_progress_entry(
    data: ProgressEntryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = ProgressEntry(user_id=current_user.id, **data.model_dump(exclude_unset=True))
    return await ProgressRepository(db).create(entry)


@router.get("/entries", response_model=list[ProgressEntryOut])
async def get_progress_entries(
    days: int = 90,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ProgressRepository(db).get_range(current_user.id, days)


@router.get("/weekly-review", response_model=WeeklyReviewOut)
async def get_weekly_review(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WeeklyReviewService(
        CheckInRepository(db), ProgressRepository(db), WorkoutRepository(db)
    )
    return await service.generate(current_user.id)
