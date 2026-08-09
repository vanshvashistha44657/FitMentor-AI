import logging
import uuid
from datetime import date, timedelta

from app.ai.provider import AIProviderError, generate_json
from app.models.fitness import DailyCheckIn, ProgressEntry, WorkoutSession
from app.repositories.checkin_repository import CheckInRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.workout_repository import WorkoutRepository

logger = logging.getLogger(__name__)

REVIEW_SYSTEM_PROMPT = """You are a fitness coach writing a concise weekly review for your \
client based on their logged data. Be specific and reference the actual numbers given. Respond \
with ONLY a JSON object: {"suggestions": ["2-4 short, actionable, specific suggestion strings"]}"""

FALLBACK_SUGGESTIONS = [
    "Keep logging daily check-ins consistently — the more data you give your coach, the sharper next week's plan gets.",
]


def _weight_trend(entries: list[ProgressEntry]) -> dict:
    weights = [e.weight_kg for e in entries if e.weight_kg is not None]
    if len(weights) < 2:
        return {"start_kg": weights[0] if weights else None, "end_kg": weights[-1] if weights else None, "change_kg": None}
    return {"start_kg": weights[0], "end_kg": weights[-1], "change_kg": round(weights[-1] - weights[0], 2)}


def _adherence_percent(checkins: list[DailyCheckIn], days: int) -> float:
    if days == 0:
        return 0.0
    return round(len(checkins) / days * 100, 1)


def _workout_score(sessions: list[WorkoutSession], target_days: int) -> float:
    if target_days == 0:
        return 0.0
    completed = sum(1 for s in sessions if s.completed)
    return round(min(completed / target_days, 1.0) * 100, 1)


class WeeklyReviewService:
    def __init__(
        self,
        checkin_repo: CheckInRepository,
        progress_repo: "ProgressRepository",
        workout_repo: WorkoutRepository,
    ):
        self.checkin_repo = checkin_repo
        self.progress_repo = progress_repo
        self.workout_repo = workout_repo

    async def generate(self, user_id: uuid.UUID, target_workout_days: int = 4) -> dict:
        checkins = await self.checkin_repo.get_range(user_id, days=7)
        progress_entries = await self.progress_repo.get_range(user_id, days=7)
        all_sessions = await self.workout_repo.get_sessions(user_id, limit=50)
        since = date.today() - timedelta(days=7)
        recent_sessions = [s for s in all_sessions if s.performed_at.date() >= since]

        weight_trend = _weight_trend(progress_entries)
        adherence = _adherence_percent(checkins, days=7)
        workout_score = _workout_score(recent_sessions, target_workout_days)

        avg_calories = None
        cal_values = [c.calories_yesterday for c in checkins if c.calories_yesterday is not None]
        if cal_values:
            avg_calories = round(sum(cal_values) / len(cal_values))

        avg_sleep = None
        sleep_values = [c.sleep_hours for c in checkins if c.sleep_hours is not None]
        if sleep_values:
            avg_sleep = round(sum(sleep_values) / len(sleep_values), 1)

        recovery_signals = [c.soreness for c in checkins if c.soreness is not None]
        recovery_score = round(100 - (sum(recovery_signals) / len(recovery_signals) * 10), 1) if recovery_signals else None

        total_volume = sum(s.total_volume_kg or 0 for s in recent_sessions)

        report = {
            "weight_trend": weight_trend,
            "adherence_percent": adherence,
            "workout_score": workout_score,
            "avg_calories": avg_calories,
            "avg_sleep_hours": avg_sleep,
            "recovery_score": recovery_score,
            "total_workout_volume_kg": round(total_volume, 1) if total_volume else None,
            "workouts_completed": sum(1 for s in recent_sessions if s.completed),
        }

        report["suggestions"] = await self._suggest(report)
        return report

    async def _suggest(self, report: dict) -> list[str]:
        try:
            result = await generate_json(REVIEW_SYSTEM_PROMPT, f"Weekly data: {report}")
            suggestions = result.get("suggestions")
            if isinstance(suggestions, list) and suggestions:
                return suggestions
            return FALLBACK_SUGGESTIONS
        except (AIProviderError, Exception) as e:  # noqa: BLE001
            logger.warning("AI weekly suggestions failed, using fallback: %s", e)
            return FALLBACK_SUGGESTIONS
