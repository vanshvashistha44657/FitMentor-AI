from pydantic import BaseModel


class GamificationProfileOut(BaseModel):
    xp: int
    level: int
    current_streak_days: int
    longest_streak_days: int
    badges: list[str]

    model_config = {"from_attributes": True}
