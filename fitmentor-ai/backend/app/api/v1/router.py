from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    chat,
    checkin,
    gamification,
    notifications,
    nutrition,
    onboarding,
    progress,
    workouts,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(workouts.router)
api_router.include_router(nutrition.router)
api_router.include_router(chat.router)
api_router.include_router(checkin.router)
api_router.include_router(progress.router)
api_router.include_router(gamification.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
