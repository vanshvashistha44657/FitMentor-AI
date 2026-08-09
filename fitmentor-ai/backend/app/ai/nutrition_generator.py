from pydantic import BaseModel

from app.models.user import UserProfile

NUTRITION_SYSTEM_PROMPT = """You are a registered dietitian-level AI nutrition coach. You build \
meal plans that respect the client's diet type, allergies, budget, and preferred cuisine — never \
a generic template. You calculate calories and macros using their stated goal (fat loss = \
moderate deficit, muscle gain = moderate surplus, recomposition = maintenance with high protein, \
etc.), current weight, and activity level. You always account for food allergies strictly — \
never include an allergen. You provide budget-friendly ingredient swaps when the client has a \
tight daily budget. You include a shopping list grouped by category.

Respond with ONLY a JSON object matching this exact structure, no markdown fences, no prose \
outside the JSON:

{
  "daily_calories": 2400,
  "protein_g": 180,
  "carbs_g": 250,
  "fat_g": 70,
  "fiber_g": 30,
  "water_liters": 3.0,
  "rationale": "2-4 sentences explaining the calorie/macro targets for this specific client",
  "meals": {
    "breakfast": [{"item": "string", "portion": "string", "calories": 400, "protein_g": 30}],
    "lunch": [{"item": "string", "portion": "string", "calories": 600, "protein_g": 45}],
    "dinner": [{"item": "string", "portion": "string", "calories": 600, "protein_g": 45}],
    "snacks": [{"item": "string", "portion": "string", "calories": 200, "protein_g": 15}],
    "pre_workout": [{"item": "string", "portion": "string", "calories": 150, "protein_g": 10}],
    "post_workout": [{"item": "string", "portion": "string", "calories": 250, "protein_g": 30}]
  },
  "supplements": ["optional list of strings, e.g. 'Whey protein — 1 scoop post-workout'"],
  "grocery_list": {
    "proteins": ["string"],
    "carbs": ["string"],
    "fats": ["string"],
    "produce": ["string"],
    "other": ["string"]
  }
}"""


class MealItem(BaseModel):
    item: str
    portion: str
    calories: int
    protein_g: int


class NutritionPlanAIResponse(BaseModel):
    daily_calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int
    water_liters: float
    rationale: str
    meals: dict[str, list[MealItem]]
    supplements: list[str] = []
    grocery_list: dict[str, list[str]]


def build_nutrition_user_prompt(profile: UserProfile) -> str:
    return f"""Client profile:
- Goal: {profile.fitness_goal}
- Weight: {profile.weight_kg}kg, Target: {profile.target_weight_kg}kg, Height: {profile.height_cm}cm
- Age: {profile.age}, Gender: {profile.gender}
- Activity level: {profile.activity_level}
- Diet type: {profile.diet_type}
- Food allergies (MUST avoid entirely): {profile.food_allergies or 'none reported'}
- Preferred cuisine: {profile.preferred_cuisine or 'no preference'}
- Daily food budget: {f'{profile.daily_budget}' if profile.daily_budget else 'no constraint specified'}
- Workout days/week: {profile.workout_days}, session duration: {profile.workout_duration_minutes} min
- Medical conditions relevant to diet: {profile.medical_conditions or 'none reported'}

Build the full daily nutrition plan now."""
