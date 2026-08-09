from app.ai.scoring import (
    calculate_bmi,
    calculate_fitness_score,
    calculate_health_score,
    calculate_lifestyle_score,
    calculate_muscle_balance_score,
    calculate_recovery_score,
)
from app.models.user import UserProfile


def make_profile(**overrides) -> UserProfile:
    defaults = dict(
        age=28,
        gender="male",
        height_cm=180,
        weight_kg=80,
        target_weight_kg=75,
        experience="1-3y",
        workout_days=4,
        workout_duration_minutes=60,
        smoking=False,
        alcohol=False,
        stress_level="moderate",
        water_intake_liters=2.0,
        daily_step_count=8000,
        sleep_time="23:00",
        wake_time="07:00",
        weak_muscles="chest",
        strong_muscles="legs,back",
    )
    defaults.update(overrides)
    return UserProfile(**defaults)


def test_calculate_bmi():
    assert calculate_bmi(80, 180) == 24.7


def test_fitness_score_rewards_experience_and_consistency():
    beginner = make_profile(experience="never", workout_days=1, workout_duration_minutes=20)
    veteran = make_profile(experience="5y+", workout_days=6, workout_duration_minutes=75)
    assert calculate_fitness_score(veteran) > calculate_fitness_score(beginner)


def test_health_score_penalizes_smoking():
    non_smoker = make_profile(smoking=False)
    smoker = make_profile(smoking=True)
    assert calculate_health_score(smoker) < calculate_health_score(non_smoker)


def test_health_score_penalizes_extreme_bmi():
    normal = make_profile(height_cm=180, weight_kg=75)
    extreme = make_profile(height_cm=180, weight_kg=140)
    assert calculate_health_score(extreme) < calculate_health_score(normal)


def test_muscle_balance_score_neutral_when_no_data():
    profile = make_profile(weak_muscles=None, strong_muscles=None)
    assert calculate_muscle_balance_score(profile) == 60.0


def test_muscle_balance_score_drops_with_more_weak_muscles():
    balanced = make_profile(weak_muscles="chest", strong_muscles="back,legs,arms")
    imbalanced = make_profile(weak_muscles="chest,back,legs", strong_muscles="arms")
    assert calculate_muscle_balance_score(imbalanced) < calculate_muscle_balance_score(balanced)


def test_lifestyle_score_rewards_step_count():
    low_steps = make_profile(daily_step_count=2000)
    high_steps = make_profile(daily_step_count=11000)
    assert calculate_lifestyle_score(high_steps) > calculate_lifestyle_score(low_steps)


def test_recovery_score_penalizes_short_sleep():
    short_sleep = make_profile(sleep_time="01:00", wake_time="06:00")  # 5h
    good_sleep = make_profile(sleep_time="22:00", wake_time="06:30")   # 8.5h
    assert calculate_recovery_score(good_sleep) > calculate_recovery_score(short_sleep)


def test_all_scores_bounded_0_to_100():
    extreme_profile = make_profile(
        smoking=True, alcohol=True, stress_level="very_high",
        daily_step_count=500, weight_kg=200, height_cm=150,
    )
    for fn in (calculate_fitness_score, calculate_health_score, calculate_lifestyle_score, calculate_recovery_score):
        score = fn(extreme_profile)
        assert 0 <= score <= 100
