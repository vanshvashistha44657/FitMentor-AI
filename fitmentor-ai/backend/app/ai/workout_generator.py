"""
Prompt construction + response validation for the AI Workout Generator.
The LLM is asked to return strict JSON matching WorkoutPlanAIResponse so a
malformed generation fails loudly (Pydantic ValidationError) instead of
silently shipping a broken plan to the user.
"""
from pydantic import BaseModel, Field

from app.models.user import UserProfile

WORKOUT_SYSTEM_PROMPT = """You are an elite strength & conditioning coach with certifications \
in exercise science (CSCS-level). You design workout programs that are safe, progressive, and \
tailored exactly to the client in front of you — never a generic template. You take injuries \
and medical conditions seriously: if the client has reported one, you avoid contraindicated \
movements and note the modification in your rationale. You always include warm-up, activation, \
main lifts, accessory work, and cooldown. You program using RPE (rate of perceived exertion, \
1-10 scale), explicit tempo (e.g. "3-1-1-0"), and rest periods in seconds. You apply progressive \
overload logic across the week and flag whether this is a deload week.

Respond with ONLY a JSON object matching this exact structure, no markdown fences, no prose \
outside the JSON:

{
  "split_type": "string (e.g. Push Pull Legs, Upper Lower, Full Body, Arnold Split, Bro Split, PHUL, PHAT, Powerbuilding)",
  "week_number": 1,
  "is_deload_week": false,
  "rationale": "2-4 sentences explaining why this split/structure fits this specific client",
  "days": [
    {
      "day_label": "string (e.g. 'Push Day A')",
      "focus": "string (e.g. 'Chest, Shoulders, Triceps')",
      "warm_up": [{"name": "string", "duration_or_reps": "string"}],
      "activation": [{"name": "string", "sets": 2, "reps": "10-12"}],
      "exercises": [
        {
          "name": "string",
          "category": "compound | isolation | cardio",
          "sets": 4,
          "reps": "6-8",
          "tempo": "3-1-1-0",
          "rest_seconds": 90,
          "target_rpe": 8,
          "notes": "optional form cue or injury modification"
        }
      ],
      "cooldown": [{"name": "string", "duration_or_reps": "string"}]
    }
  ]
}

Generate exactly as many "days" entries as the client's stated workout_days per week."""


class WarmupItem(BaseModel):
    name: str
    duration_or_reps: str


class ActivationItem(BaseModel):
    name: str
    sets: int
    reps: str


class ExerciseItem(BaseModel):
    name: str
    category: str
    sets: int
    reps: str
    tempo: str
    rest_seconds: int
    target_rpe: float = Field(ge=1, le=10)
    notes: str | None = None


class WorkoutDay(BaseModel):
    day_label: str
    focus: str
    warm_up: list[WarmupItem]
    activation: list[ActivationItem] = []
    exercises: list[ExerciseItem]
    cooldown: list[WarmupItem]


class WorkoutPlanAIResponse(BaseModel):
    split_type: str
    week_number: int = 1
    is_deload_week: bool = False
    rationale: str
    days: list[WorkoutDay]


def build_workout_user_prompt(profile: UserProfile, week_number: int, is_deload_week: bool) -> str:
    return f"""Client profile:
- Goal: {profile.fitness_goal}
- Fitness level: {profile.fitness_level} ({profile.experience} experience)
- Age: {profile.age}, Gender: {profile.gender}
- Height: {profile.height_cm}cm, Weight: {profile.weight_kg}kg, Target: {profile.target_weight_kg}kg
- Body fat: {profile.body_fat_percent or 'unknown'}%
- Medical conditions: {profile.medical_conditions or 'none reported'}
- Past injuries: {profile.past_injuries or 'none reported'}
- Workout location: {profile.workout_location}
- Equipment available: {profile.gym_equipment or 'bodyweight only'}
- Days per week: {profile.workout_days}
- Session duration: {profile.workout_duration_minutes} minutes
- Favorite exercises: {profile.favorite_exercises or 'none specified'}
- Exercises to avoid: {profile.disliked_exercises or 'none specified'}
- Target muscles to prioritize: {profile.target_muscles or 'none specified'}
- Weak muscles needing extra volume: {profile.weak_muscles or 'none specified'}

This is week {week_number} of the program. {"This IS a deload week — reduce volume/intensity by roughly 40%." if is_deload_week else "This is a normal training week."}

Design the full program now."""
