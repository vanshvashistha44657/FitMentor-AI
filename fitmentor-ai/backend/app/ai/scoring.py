"""
Score calculations are deterministic, not LLM-generated — scores must be
reproducible and auditable. The AI's job (see scoring_service.py) is to
*explain* these numbers in natural language, not compute them.
"""
from app.models.user import UserProfile

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.9,
}

EXPERIENCE_WEIGHTS = {
    "never": 0.1,
    "<1y": 0.35,
    "1-3y": 0.6,
    "3-5y": 0.8,
    "5y+": 1.0,
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def calculate_fitness_score(profile: UserProfile) -> float:
    """Weighted blend of training experience, consistency capacity (days/week),
    and session duration adequacy for stated goal."""
    experience_component = EXPERIENCE_WEIGHTS.get(profile.experience or "never", 0.1) * 40
    days = profile.workout_days or 0
    frequency_component = min(days / 6, 1.0) * 30
    duration = profile.workout_duration_minutes or 0
    duration_component = min(duration / 75, 1.0) * 30
    score = experience_component + frequency_component + duration_component
    return round(min(score, 100), 1)


def calculate_health_score(profile: UserProfile) -> float:
    """Penalizes risk factors (smoking, extreme BMI, high stress) and rewards
    protective factors (hydration, activity, sleep window)."""
    score = 100.0

    if profile.height_cm and profile.weight_kg:
        bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
        if bmi < 18.5 or bmi > 30:
            score -= 20
        elif bmi > 27:
            score -= 10

    if profile.smoking:
        score -= 20
    if profile.alcohol:
        score -= 8

    stress_penalty = {"low": 0, "moderate": 5, "high": 15, "very_high": 25}
    score -= stress_penalty.get((profile.stress_level or "moderate").lower(), 5)

    if profile.water_intake_liters is not None:
        if profile.water_intake_liters < 1.5:
            score -= 10
        elif profile.water_intake_liters >= 2.5:
            score += 5

    if profile.medical_conditions and profile.medical_conditions.strip().lower() not in ("", "none", "n/a"):
        score -= 5  # not a penalty for having a condition — reflects added complexity/risk to manage

    return round(max(0, min(score, 100)), 1)


def calculate_muscle_balance_score(profile: UserProfile) -> float:
    """Compares self-reported weak vs strong muscle groups — larger the gap
    reported, lower the balance score. This is a starting estimate; it
    should be refined by the AI generator once workout logs exist."""
    weak = {m.strip().lower() for m in (profile.weak_muscles or "").split(",") if m.strip()}
    strong = {m.strip().lower() for m in (profile.strong_muscles or "").split(",") if m.strip()}

    if not weak and not strong:
        return 60.0  # neutral baseline — no data yet

    imbalance_ratio = len(weak) / max(len(weak) + len(strong), 1)
    score = 100 - (imbalance_ratio * 60)
    return round(max(0, min(score, 100)), 1)


def calculate_lifestyle_score(profile: UserProfile) -> float:
    """Sleep consistency, step count, occupation activity, and stress combined."""
    score = 100.0

    if profile.daily_step_count is not None:
        if profile.daily_step_count < 4000:
            score -= 20
        elif profile.daily_step_count < 7000:
            score -= 10
        elif profile.daily_step_count >= 10000:
            score += 5

    stress_penalty = {"low": 0, "moderate": 8, "high": 18, "very_high": 28}
    score -= stress_penalty.get((profile.stress_level or "moderate").lower(), 8)

    if profile.occupation and any(k in profile.occupation.lower() for k in ["desk", "office", "driver", "sedentary"]):
        score -= 8

    return round(max(0, min(score, 100)), 1)


def calculate_recovery_score(profile: UserProfile) -> float:
    """Estimated from sleep window length and stated stress — real recovery
    scoring improves once daily check-ins (sleep hours, soreness) accumulate."""
    score = 70.0  # neutral baseline pending check-in data

    if profile.sleep_time and profile.wake_time:
        try:
            sh, sm = map(int, profile.sleep_time.split(":"))
            wh, wm = map(int, profile.wake_time.split(":"))
            sleep_minutes = (sh * 60 + sm)
            wake_minutes = (wh * 60 + wm)
            duration = (wake_minutes - sleep_minutes) % (24 * 60)
            duration_hours = duration / 60
            if duration_hours < 6:
                score -= 20
            elif duration_hours >= 7.5:
                score += 15
        except (ValueError, AttributeError):
            pass

    stress_penalty = {"low": 0, "moderate": 5, "high": 15, "very_high": 25}
    score -= stress_penalty.get((profile.stress_level or "moderate").lower(), 5)

    return round(max(0, min(score, 100)), 1)


def calculate_all_scores(profile: UserProfile) -> dict[str, float]:
    return {
        "fitness_score": calculate_fitness_score(profile),
        "health_score": calculate_health_score(profile),
        "muscle_balance_score": calculate_muscle_balance_score(profile),
        "lifestyle_score": calculate_lifestyle_score(profile),
        "recovery_score": calculate_recovery_score(profile),
    }
