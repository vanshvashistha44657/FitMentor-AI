"""
Import every model here so Alembic's autogenerate (via db.session.Base.metadata)
picks up all tables. Do not remove imports even if they look unused.
"""
from app.models.engagement import ChatMessage, GamificationProfile, Notification  # noqa: F401
from app.models.fitness import (  # noqa: F401
    AIScore,
    DailyCheckIn,
    Exercise,
    NutritionPlan,
    ProgressEntry,
    WorkoutPlan,
    WorkoutSession,
)
from app.models.user import User, UserProfile  # noqa: F401
