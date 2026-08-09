"""
Central place that awards XP and updates streaks/badges. Other services
(workouts, nutrition adherence, daily check-ins) call into this rather than
touching GamificationProfile directly, so the leveling curve and badge
rules live in exactly one place.
"""
import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import GamificationProfile
from app.models.fitness import DailyCheckIn

XP_PER_WORKOUT = 50
XP_PER_CHECKIN = 15
XP_PER_LEVEL = 200  # flat curve for simplicity; can move to a curve later

BADGE_RULES = {
    "first_workout": lambda profile: profile.xp >= XP_PER_WORKOUT,
    "week_streak": lambda profile: profile.current_streak_days >= 7,
    "month_streak": lambda profile: profile.current_streak_days >= 30,
    "level_5": lambda profile: profile.level >= 5,
    "level_10": lambda profile: profile.level >= 10,
}


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create(self, user_id: uuid.UUID) -> GamificationProfile:
        result = await self.db.execute(
            select(GamificationProfile).where(GamificationProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = GamificationProfile(user_id=user_id, badges=[])
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        return profile

    def _apply_xp(self, profile: GamificationProfile, amount: int) -> None:
        profile.xp += amount
        profile.level = max(1, profile.xp // XP_PER_LEVEL + 1)

    def _update_badges(self, profile: GamificationProfile) -> None:
        current = set(profile.badges or [])
        for badge_code, rule in BADGE_RULES.items():
            if badge_code not in current and rule(profile):
                current.add(badge_code)
        profile.badges = list(current)

    async def award_workout_completion(self, user_id: uuid.UUID) -> GamificationProfile:
        profile = await self._get_or_create(user_id)
        self._apply_xp(profile, XP_PER_WORKOUT)
        self._update_badges(profile)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def award_checkin_and_update_streak(self, user_id: uuid.UUID) -> GamificationProfile:
        profile = await self._get_or_create(user_id)

        # Determine streak continuity using the two most recent check-ins.
        result = await self.db.execute(
            select(DailyCheckIn.checkin_date)
            .where(DailyCheckIn.user_id == user_id)
            .order_by(DailyCheckIn.checkin_date.desc())
            .limit(2)
        )
        recent_dates = [row[0] for row in result.all()]

        if len(recent_dates) >= 2 and recent_dates[0] - recent_dates[1] == timedelta(days=1):
            profile.current_streak_days += 1
        elif len(recent_dates) == 1:
            profile.current_streak_days = 1
        else:
            profile.current_streak_days = 1  # first check-in ever, or streak broken

        profile.longest_streak_days = max(profile.longest_streak_days, profile.current_streak_days)

        self._apply_xp(profile, XP_PER_CHECKIN)
        self._update_badges(profile)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_profile(self, user_id: uuid.UUID) -> GamificationProfile:
        return await self._get_or_create(user_id)
