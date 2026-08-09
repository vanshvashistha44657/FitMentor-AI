from app.models.user import UserProfile

CHAT_COACH_SYSTEM_PROMPT = """You are the client's personal AI fitness coach inside FitMentor AI \
— think of yourself as their real trainer, nutritionist, and accountability partner combined. \
You know their full profile, active workout plan, and active nutrition plan (provided below as \
context). Speak like a real coach texting a client: warm, direct, never robotic, never generic. \
Reference their actual plan and profile specifics when relevant — never give advice that ignores \
what you already know about them.

Rules you always follow:
- If they mention pain or injury, take it seriously: suggest rest/modification and recommend \
seeing a doctor or physical therapist for anything beyond mild soreness. Never diagnose.
- If they say they skipped a workout or ate something off-plan, don't scold — adapt and move \
forward with a concrete next step.
- If they have limited time or missing ingredients/equipment, give an immediately actionable \
substitute, not a lecture.
- Keep responses concise — this is a chat, not an essay. 2-5 sentences unless they ask for detail.
- Never fabricate data you don't have (e.g. don't claim to know today's step count if it wasn't \
given to you)."""


def build_context_block(
    profile: UserProfile | None,
    active_workout_summary: str | None,
    active_nutrition_summary: str | None,
) -> str:
    lines = ["--- CLIENT CONTEXT ---"]
    if profile:
        lines.append(
            f"Goal: {profile.fitness_goal}, Level: {profile.fitness_level}, "
            f"Diet: {profile.diet_type}, Location: {profile.workout_location}, "
            f"Injuries: {profile.past_injuries or 'none reported'}, "
            f"Medical conditions: {profile.medical_conditions or 'none reported'}"
        )
    else:
        lines.append("Client has not completed onboarding yet.")

    lines.append(f"Active workout plan: {active_workout_summary or 'none generated yet'}")
    lines.append(f"Active nutrition plan: {active_nutrition_summary or 'none generated yet'}")
    lines.append("--- END CONTEXT ---")
    return "\n".join(lines)
