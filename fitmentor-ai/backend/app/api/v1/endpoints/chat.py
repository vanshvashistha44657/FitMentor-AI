from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.nutrition_repository import NutritionRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.chat import ChatMessageOut, ChatSendRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/coach/chat", tags=["AI Chat Coach"])


@router.post("/send", response_model=ChatMessageOut)
async def send_chat_message(
    data: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await ProfileRepository(db).get_by_user_id(current_user.id)
    active_workout = await WorkoutRepository(db).get_active_plan(current_user.id)
    active_nutrition = await NutritionRepository(db).get_active(current_user.id)

    service = ChatService(ChatRepository(db))
    return await service.send_message(
        current_user.id, data.message, profile, active_workout, active_nutrition
    )


@router.get("/history", response_model=list[ChatMessageOut])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(ChatRepository(db))
    return await service.get_history(current_user.id)
