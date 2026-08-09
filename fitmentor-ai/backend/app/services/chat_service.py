import uuid

from fastapi import HTTPException, status

from app.ai.chat_coach import CHAT_COACH_SYSTEM_PROMPT, build_context_block
from app.ai.provider import AIProviderError, get_ai_provider
from app.models.engagement import ChatMessage, MessageRole
from app.models.fitness import NutritionPlan, WorkoutPlan
from app.models.user import UserProfile
from app.repositories.chat_repository import ChatRepository


def _summarize_workout(plan: WorkoutPlan | None) -> str | None:
    if not plan:
        return None
    return f"{plan.split_type} (week {plan.week_number}, {'deload' if plan.is_deload_week else 'normal'})"


def _summarize_nutrition(plan: NutritionPlan | None) -> str | None:
    if not plan:
        return None
    return f"{plan.daily_calories} kcal/day, {plan.protein_g}g protein, {plan.carbs_g}g carbs, {plan.fat_g}g fat"


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    async def send_message(
        self,
        user_id: uuid.UUID,
        user_message: str,
        profile: UserProfile | None,
        active_workout: WorkoutPlan | None,
        active_nutrition: NutritionPlan | None,
    ) -> ChatMessage:
        history = await self.repo.get_recent_history(user_id, limit=20)

        context_block = build_context_block(
            profile, _summarize_workout(active_workout), _summarize_nutrition(active_nutrition)
        )

        transcript_lines = [context_block, ""]
        for msg in history:
            speaker = "Client" if msg.role == MessageRole.USER else "Coach"
            transcript_lines.append(f"{speaker}: {msg.content}")
        transcript_lines.append(f"Client: {user_message}")
        transcript_lines.append("Coach:")

        # Persist the user's message immediately, regardless of AI outcome —
        # a failed AI call shouldn't lose what the client typed.
        await self.repo.add_message(
            ChatMessage(user_id=user_id, role=MessageRole.USER, content=user_message)
        )

        try:
            provider = get_ai_provider()
            reply_text = await provider.generate(CHAT_COACH_SYSTEM_PROMPT, "\n".join(transcript_lines))
        except AIProviderError as e:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Your AI coach is temporarily unavailable: {e}")
        except Exception as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Your AI coach couldn't respond: {e}")

        assistant_message = await self.repo.add_message(
            ChatMessage(
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=reply_text.strip(),
                context_snapshot={
                    "workout": _summarize_workout(active_workout),
                    "nutrition": _summarize_nutrition(active_nutrition),
                },
            )
        )
        return assistant_message

    async def get_history(self, user_id: uuid.UUID, limit: int = 50) -> list[ChatMessage]:
        return await self.repo.get_paginated(user_id, limit)
