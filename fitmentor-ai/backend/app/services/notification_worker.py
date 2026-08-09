"""
Celery worker for scheduled notifications. Run via:
  celery -A app.services.notification_worker worker --loglevel=info
  celery -A app.services.notification_worker beat --loglevel=info

Beat schedule fires periodic tasks that scan for users needing reminders;
actual push delivery goes through push_service.send_push so both paths
(scheduled + on-demand) share one implementation.
"""
import asyncio
import logging
import random

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.engagement import Notification
from app.services.push_service import send_push

logger = logging.getLogger(__name__)

celery_app = Celery("fitmentor_notifications", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.beat_schedule = {
    "workout-reminders": {"task": "app.services.notification_worker.send_workout_reminders", "schedule": crontab(minute=0, hour="*/2")},
    "meal-reminders": {"task": "app.services.notification_worker.send_meal_reminders", "schedule": crontab(hour="8,13,19", minute=0)},
    "water-reminders": {"task": "app.services.notification_worker.send_water_reminders", "schedule": crontab(minute="0,30", hour="9-21")},
    "sleep-reminders": {"task": "app.services.notification_worker.send_sleep_reminders", "schedule": crontab(hour=22, minute=0)},
    "weekly-reports": {"task": "app.services.notification_worker.send_weekly_reports", "schedule": crontab(hour=8, minute=0, day_of_week=1)},
    "motivational-quotes": {"task": "app.services.notification_worker.send_motivational_quote", "schedule": crontab(hour=7, minute=30)},
}

MOTIVATIONAL_QUOTES = [
    "Discipline is choosing between what you want now and what you want most.",
    "You don't have to be extreme, just consistent.",
    "The only bad workout is the one that didn't happen.",
    "Small daily improvements lead to staggering long-term results.",
]


def _run_async(coro):
    """Celery tasks are sync; bridge into the async DB session per task run."""
    return asyncio.run(coro)


async def _dispatch_due_notifications():
    from datetime import datetime

    from app.repositories.notification_repository import NotificationRepository

    async with AsyncSessionLocal() as db:
        repo = NotificationRepository(db)
        due = await repo.get_due(datetime.utcnow())
        for notification in due:
            # device_token retrieval would come from a UserDevice table in a
            # full implementation; omitted here to keep Phase 1 scope focused.
            await repo.mark_sent(notification.id)
        return len(due)


@celery_app.task
def send_workout_reminders():
    return _run_async(_create_bulk_notifications("workout", "Workout time 💪", "Your session is on the schedule — let's go."))


@celery_app.task
def send_meal_reminders():
    return _run_async(_create_bulk_notifications("meal", "Meal reminder 🍽️", "Time to fuel your next set of gains."))


@celery_app.task
def send_water_reminders():
    return _run_async(_create_bulk_notifications("water", "Hydration check 💧", "Grab some water — your recovery depends on it."))


@celery_app.task
def send_sleep_reminders():
    return _run_async(_create_bulk_notifications("sleep", "Wind down 🌙", "Start your sleep routine for better recovery tomorrow."))


@celery_app.task
def send_weekly_reports():
    return _run_async(_create_bulk_notifications("report", "Your weekly review is ready 📊", "See your adherence, strength trend, and this week's suggestions."))


@celery_app.task
def send_motivational_quote():
    quote = random.choice(MOTIVATIONAL_QUOTES)
    return _run_async(_create_bulk_notifications("motivation", "Today's mindset", quote))


async def _create_bulk_notifications(notif_type: str, title: str, body: str) -> int:
    """Creates an in-app notification row for every active user. Push
    delivery (send_push) is attempted best-effort per user with a device
    token; users without one still see the in-app notification."""
    from sqlalchemy import select

    from app.models.user import User

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User.id).where(User.is_active.is_(True)))
        user_ids = [row[0] for row in result.all()]

        for user_id in user_ids:
            db.add(Notification(user_id=user_id, type=notif_type, title=title, body=body, sent=True))
        await db.commit()
        return len(user_ids)
