import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WorkoutPlan(Base):
    """A generated multi-week training plan (e.g. PPL, Upper/Lower)."""
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    split_type: Mapped[str] = mapped_column(String(50))  # PPL, Upper/Lower, Full Body, etc.
    goal: Mapped[str] = mapped_column(String(60))
    week_number: Mapped[int] = mapped_column(Integer, default=1)
    is_deload_week: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Full structured plan (days -> exercises -> sets/reps/tempo/rest/RPE) stored as JSON
    # for flexibility, since exercise structure varies significantly by split/goal.
    plan_data: Mapped[dict] = mapped_column(JSON)

    ai_rationale: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    sessions: Mapped[list["WorkoutSession"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class WorkoutSession(Base):
    """A single completed/logged workout instance."""
    __tablename__ = "workout_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    plan_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True)

    day_label: Mapped[str] = mapped_column(String(60))  # e.g. "Push Day A"
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    total_volume_kg: Mapped[float | None] = mapped_column(nullable=True)
    avg_rpe: Mapped[float | None] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)

    # Actual logged sets: [{exercise, weight, reps, rpe, notes}]
    log_data: Mapped[dict] = mapped_column(JSON)

    plan: Mapped["WorkoutPlan"] = relationship(back_populates="sessions")


class Exercise(Base):
    """Master exercise database (used by admin + AI generator)."""
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(40))  # compound | isolation | cardio | mobility
    primary_muscle: Mapped[str] = mapped_column(String(60))
    secondary_muscles: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_needed: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20))  # beginner | intermediate | advanced
    instructions: Mapped[str | None] = mapped_column(String, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    daily_calories: Mapped[int] = mapped_column(Integer)
    protein_g: Mapped[int] = mapped_column(Integer)
    carbs_g: Mapped[int] = mapped_column(Integer)
    fat_g: Mapped[int] = mapped_column(Integer)
    fiber_g: Mapped[int] = mapped_column(Integer)
    water_liters: Mapped[float] = mapped_column(Float)

    # Meals keyed by slot: breakfast/lunch/dinner/snacks/pre_workout/post_workout
    meal_plan: Mapped[dict] = mapped_column(JSON)
    grocery_list: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_rationale: Mapped[str | None] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class DailyCheckIn(Base):
    __tablename__ = "daily_checkins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    checkin_date: Mapped[date] = mapped_column(Date, default=date.today)

    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    sleep_hours: Mapped[float | None] = mapped_column(nullable=True)
    energy_level: Mapped[int | None] = mapped_column(nullable=True)   # 1-10
    mood: Mapped[int | None] = mapped_column(nullable=True)           # 1-10
    soreness: Mapped[int | None] = mapped_column(nullable=True)       # 1-10
    stress: Mapped[int | None] = mapped_column(nullable=True)         # 1-10
    water_liters: Mapped[float | None] = mapped_column(nullable=True)
    calories_yesterday: Mapped[int | None] = mapped_column(nullable=True)
    workout_completed: Mapped[bool | None] = mapped_column(nullable=True)
    steps: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ProgressEntry(Base):
    """Time-series data point for charts: weight, body fat, measurements, photos."""
    __tablename__ = "progress_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    entry_date: Mapped[date] = mapped_column(Date, default=date.today)

    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    body_fat_percent: Mapped[float | None] = mapped_column(nullable=True)
    measurements: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # chest, waist, arms, etc.
    photo_urls: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AIScore(Base):
    """Fitness/Health/Muscle-Balance/Lifestyle/Recovery scores with explanations."""
    __tablename__ = "ai_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    fitness_score: Mapped[float] = mapped_column(Float)
    health_score: Mapped[float] = mapped_column(Float)
    muscle_balance_score: Mapped[float] = mapped_column(Float)
    lifestyle_score: Mapped[float] = mapped_column(Float)
    recovery_score: Mapped[float] = mapped_column(Float)

    explanations: Mapped[dict] = mapped_column(JSON)  # {score_name: explanation_text}

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
