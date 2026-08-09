import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    auth_provider: Mapped[AuthProvider] = mapped_column(Enum(AuthProvider), default=AuthProvider.EMAIL)
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    """
    Everything collected during onboarding. One-to-one with User.
    Kept separate from User so auth concerns never mix with fitness data.
    """
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Basic details
    age: Mapped[int | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    target_weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    body_fat_percent: Mapped[float | None] = mapped_column(nullable=True)

    # Goals & experience
    fitness_goal: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fitness_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Health
    medical_conditions: Mapped[str | None] = mapped_column(String, nullable=True)
    past_injuries: Mapped[str | None] = mapped_column(String, nullable=True)
    medications: Mapped[str | None] = mapped_column(String, nullable=True)
    allergies: Mapped[str | None] = mapped_column(String, nullable=True)

    # Diet
    diet_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    food_allergies: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_cuisine: Mapped[str | None] = mapped_column(String(120), nullable=True)
    daily_budget: Mapped[float | None] = mapped_column(nullable=True)

    # Training logistics
    workout_location: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gym_equipment: Mapped[str | None] = mapped_column(String, nullable=True)
    workout_time: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workout_days: Mapped[int | None] = mapped_column(nullable=True)
    workout_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)

    # Lifestyle
    sleep_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    wake_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    stress_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    water_intake_liters: Mapped[float | None] = mapped_column(nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    smoking: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    alcohol: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    daily_step_count: Mapped[int | None] = mapped_column(nullable=True)

    # Preferences
    favorite_exercises: Mapped[str | None] = mapped_column(String, nullable=True)
    disliked_exercises: Mapped[str | None] = mapped_column(String, nullable=True)
    target_muscles: Mapped[str | None] = mapped_column(String, nullable=True)
    weak_muscles: Mapped[str | None] = mapped_column(String, nullable=True)
    strong_muscles: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="profile")
