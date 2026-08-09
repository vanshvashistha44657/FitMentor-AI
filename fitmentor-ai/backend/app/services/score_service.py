"""
Orchestrates the "AI Analysis" step: compute scores deterministically
(app.ai.scoring), then ask the LLM to explain them in plain language.
If the AI call fails (no key configured, provider error, etc.) we fall back
to template explanations rather than failing onboarding — a user should
never be blocked from reaching their dashboard because an LLM call failed.
"""
import logging

from app.ai.provider import AIProviderError, generate_json
from app.ai.scoring import calculate_all_scores
from app.models.fitness import AIScore
from app.models.user import UserProfile
from app.repositories.profile_repository import ScoreRepository

logger = logging.getLogger(__name__)

SCORE_EXPLAINER_SYSTEM_PROMPT = """You are a certified fitness coach explaining a client's \
onboarding scores. Be specific, encouraging but honest, and reference the actual numbers \
you're given. Never invent data you weren't given. If a score reflects a health risk factor \
(smoking, poor sleep, high stress), name it plainly and note it's worth discussing with a \
doctor if relevant — do not diagnose. Respond ONLY with a JSON object with these exact keys: \
fitness_score, health_score, muscle_balance_score, lifestyle_score, recovery_score — each \
value a 2-3 sentence explanation string."""

FALLBACK_EXPLANATIONS = {
    "fitness_score": "Reflects your training experience, weekly frequency, and session length. This will rise as you log consistent workouts.",
    "health_score": "A snapshot based on BMI range, lifestyle risk factors, and hydration. Improves with consistent healthy habits over time.",
    "muscle_balance_score": "Estimated from the muscle groups you told us are strong vs. weak. Will sharpen once we have real workout volume data per muscle group.",
    "lifestyle_score": "Based on daily steps, occupation activity level, and stress. Small daily movement changes move this fastest.",
    "recovery_score": "Estimated from your sleep window and stress level. Daily check-ins will make this far more accurate.",
}


class ScoreService:
    def __init__(self, repo: ScoreRepository):
        self.repo = repo

    async def generate_and_save(self, user_id, profile: UserProfile) -> AIScore:
        raw_scores = calculate_all_scores(profile)
        explanations = await self._explain(raw_scores)

        score = AIScore(
            user_id=user_id,
            fitness_score=raw_scores["fitness_score"],
            health_score=raw_scores["health_score"],
            muscle_balance_score=raw_scores["muscle_balance_score"],
            lifestyle_score=raw_scores["lifestyle_score"],
            recovery_score=raw_scores["recovery_score"],
            explanations=explanations,
        )
        return await self.repo.create(score)

    async def _explain(self, raw_scores: dict[str, float]) -> dict[str, str]:
        try:
            user_prompt = f"Here are the client's scores (0-100 scale): {raw_scores}. Explain each one."
            result = await generate_json(SCORE_EXPLAINER_SYSTEM_PROMPT, user_prompt)
            # Validate the AI returned all expected keys; fall back per-key if not.
            return {key: result.get(key, FALLBACK_EXPLANATIONS[key]) for key in FALLBACK_EXPLANATIONS}
        except (AIProviderError, Exception) as e:  # noqa: BLE001 — deliberate broad catch, see docstring
            logger.warning("AI score explanation failed, using fallback text: %s", e)
            return dict(FALLBACK_EXPLANATIONS)
