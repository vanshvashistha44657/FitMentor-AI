"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    auth_provider = postgresql.ENUM("EMAIL", "GOOGLE", name="authprovider")
    subscription_tier = postgresql.ENUM("FREE", "PRO", "ELITE", name="subscriptiontier")
    message_role = postgresql.ENUM("USER", "ASSISTANT", "SYSTEM", name="messagerole")

    # NOTE: we deliberately do NOT call .create() on these here. Alembic's
    # op.create_table() below auto-emits CREATE TYPE the first time each
    # enum is used as a column type (via SQLAlchemy's before_create event),
    # with checkfirst=False. Pre-creating them manually causes a duplicate
    # "type already exists" error on every run, including a fresh database.

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("auth_provider", auth_provider, nullable=False),
        sa.Column("google_sub", sa.String(255), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_onboarded", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("subscription_tier", subscription_tier, nullable=False, server_default="FREE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("gender", sa.String(30), nullable=True),
        sa.Column("height_cm", sa.Float, nullable=True),
        sa.Column("weight_kg", sa.Float, nullable=True),
        sa.Column("target_weight_kg", sa.Float, nullable=True),
        sa.Column("body_fat_percent", sa.Float, nullable=True),
        sa.Column("fitness_goal", sa.String(60), nullable=True),
        sa.Column("fitness_level", sa.String(30), nullable=True),
        sa.Column("experience", sa.String(30), nullable=True),
        sa.Column("medical_conditions", sa.String, nullable=True),
        sa.Column("past_injuries", sa.String, nullable=True),
        sa.Column("medications", sa.String, nullable=True),
        sa.Column("allergies", sa.String, nullable=True),
        sa.Column("diet_type", sa.String(30), nullable=True),
        sa.Column("food_allergies", sa.String, nullable=True),
        sa.Column("preferred_cuisine", sa.String(120), nullable=True),
        sa.Column("daily_budget", sa.Float, nullable=True),
        sa.Column("workout_location", sa.String(30), nullable=True),
        sa.Column("gym_equipment", sa.String, nullable=True),
        sa.Column("workout_time", sa.String(30), nullable=True),
        sa.Column("workout_days", sa.Integer, nullable=True),
        sa.Column("workout_duration_minutes", sa.Integer, nullable=True),
        sa.Column("sleep_time", sa.String(10), nullable=True),
        sa.Column("wake_time", sa.String(10), nullable=True),
        sa.Column("stress_level", sa.String(20), nullable=True),
        sa.Column("water_intake_liters", sa.Float, nullable=True),
        sa.Column("occupation", sa.String(120), nullable=True),
        sa.Column("activity_level", sa.String(30), nullable=True),
        sa.Column("smoking", sa.Boolean, nullable=True),
        sa.Column("alcohol", sa.Boolean, nullable=True),
        sa.Column("daily_step_count", sa.Integer, nullable=True),
        sa.Column("favorite_exercises", sa.String, nullable=True),
        sa.Column("disliked_exercises", sa.String, nullable=True),
        sa.Column("target_muscles", sa.String, nullable=True),
        sa.Column("weak_muscles", sa.String, nullable=True),
        sa.Column("strong_muscles", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("primary_muscle", sa.String(60), nullable=False),
        sa.Column("secondary_muscles", sa.String, nullable=True),
        sa.Column("equipment_needed", sa.String, nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("instructions", sa.String, nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
    )

    op.create_table(
        "workout_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("split_type", sa.String(50), nullable=False),
        sa.Column("goal", sa.String(60), nullable=False),
        sa.Column("week_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_deload_week", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("plan_data", postgresql.JSON, nullable=False),
        sa.Column("ai_rationale", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "workout_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("day_label", sa.String(60), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("total_volume_kg", sa.Float, nullable=True),
        sa.Column("avg_rpe", sa.Float, nullable=True),
        sa.Column("completed", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("log_data", postgresql.JSON, nullable=False),
    )

    op.create_table(
        "nutrition_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("daily_calories", sa.Integer, nullable=False),
        sa.Column("protein_g", sa.Integer, nullable=False),
        sa.Column("carbs_g", sa.Integer, nullable=False),
        sa.Column("fat_g", sa.Integer, nullable=False),
        sa.Column("fiber_g", sa.Integer, nullable=False),
        sa.Column("water_liters", sa.Float, nullable=False),
        sa.Column("meal_plan", postgresql.JSON, nullable=False),
        sa.Column("grocery_list", postgresql.JSON, nullable=True),
        sa.Column("ai_rationale", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "daily_checkins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkin_date", sa.Date, nullable=False),
        sa.Column("weight_kg", sa.Float, nullable=True),
        sa.Column("sleep_hours", sa.Float, nullable=True),
        sa.Column("energy_level", sa.Integer, nullable=True),
        sa.Column("mood", sa.Integer, nullable=True),
        sa.Column("soreness", sa.Integer, nullable=True),
        sa.Column("stress", sa.Integer, nullable=True),
        sa.Column("water_liters", sa.Float, nullable=True),
        sa.Column("calories_yesterday", sa.Integer, nullable=True),
        sa.Column("workout_completed", sa.Boolean, nullable=True),
        sa.Column("steps", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "progress_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("weight_kg", sa.Float, nullable=True),
        sa.Column("body_fat_percent", sa.Float, nullable=True),
        sa.Column("measurements", postgresql.JSON, nullable=True),
        sa.Column("photo_urls", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "ai_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fitness_score", sa.Float, nullable=False),
        sa.Column("health_score", sa.Float, nullable=False),
        sa.Column("muscle_balance_score", sa.Float, nullable=False),
        sa.Column("lifestyle_score", sa.Float, nullable=False),
        sa.Column("recovery_score", sa.Float, nullable=False),
        sa.Column("explanations", postgresql.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", message_role, nullable=False),
        sa.Column("content", sa.String, nullable=False),
        sa.Column("context_snapshot", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "gamification_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("current_streak_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("longest_streak_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("badges", postgresql.JSON, nullable=False, server_default="[]"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("body", sa.String(500), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("read", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    for col in ("user_id",):
        pass  # indexes below

    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])
    op.create_index("ix_workout_plans_user_id", "workout_plans", ["user_id"])
    op.create_index("ix_workout_sessions_user_id", "workout_sessions", ["user_id"])
    op.create_index("ix_nutrition_plans_user_id", "nutrition_plans", ["user_id"])
    op.create_index("ix_daily_checkins_user_id", "daily_checkins", ["user_id"])
    op.create_index("ix_progress_entries_user_id", "progress_entries", ["user_id"])
    op.create_index("ix_ai_scores_user_id", "ai_scores", ["user_id"])
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("gamification_profiles")
    op.drop_table("chat_messages")
    op.drop_table("ai_scores")
    op.drop_table("progress_entries")
    op.drop_table("daily_checkins")
    op.drop_table("nutrition_plans")
    op.drop_table("workout_sessions")
    op.drop_table("workout_plans")
    op.drop_table("exercises")
    op.drop_table("user_profiles")
    op.drop_table("users")

    postgresql.ENUM(name="messagerole").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="subscriptiontier").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="authprovider").drop(op.get_bind(), checkfirst=True)
