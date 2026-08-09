from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository, ScoreRepository
from app.schemas.onboarding import AIScoreOut, OnboardingRequest, UserProfileOut
from app.services.score_service import ScoreService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/complete", response_model=AIScoreOut)
async def complete_onboarding(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Saves the onboarding questionnaire as the user's profile, marks the
    account onboarded, then runs AI analysis to produce the five headline
    scores the dashboard opens with.
    """
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.upsert(current_user.id, data.model_dump())

    current_user.is_onboarded = True
    db.add(current_user)
    await db.commit()

    score_service = ScoreService(ScoreRepository(db))
    score = await score_service.generate_and_save(current_user.id, profile)
    return score


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_user_id(current_user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(404, "Profile not found — complete onboarding first")
    return profile


@router.get("/scores/latest", response_model=AIScoreOut)
async def get_latest_scores(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    score_repo = ScoreRepository(db)
    score = await score_repo.get_latest(current_user.id)
    if not score:
        from fastapi import HTTPException
        raise HTTPException(404, "No scores yet — complete onboarding first")
    return score
