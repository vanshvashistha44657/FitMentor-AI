"""
Seeds the exercise database and creates a default admin account.
Run with: python -m app.db.seed
"""
import asyncio

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.fitness import Exercise
from app.models.user import AuthProvider, User

EXERCISES = [
    # (name, category, primary_muscle, equipment, difficulty)
    ("Barbell Back Squat", "compound", "quadriceps", "barbell, rack", "intermediate"),
    ("Barbell Bench Press", "compound", "chest", "barbell, bench", "intermediate"),
    ("Conventional Deadlift", "compound", "posterior chain", "barbell", "advanced"),
    ("Overhead Press", "compound", "shoulders", "barbell", "intermediate"),
    ("Pull-Up", "compound", "back", "pull-up bar", "intermediate"),
    ("Barbell Row", "compound", "back", "barbell", "intermediate"),
    ("Dumbbell Lunge", "compound", "quadriceps", "dumbbells", "beginner"),
    ("Push-Up", "compound", "chest", "bodyweight", "beginner"),
    ("Bodyweight Squat", "compound", "quadriceps", "bodyweight", "beginner"),
    ("Dumbbell Bicep Curl", "isolation", "biceps", "dumbbells", "beginner"),
    ("Triceps Rope Pushdown", "isolation", "triceps", "cable machine", "beginner"),
    ("Leg Press", "compound", "quadriceps", "leg press machine", "beginner"),
    ("Lat Pulldown", "compound", "back", "cable machine", "beginner"),
    ("Dumbbell Lateral Raise", "isolation", "shoulders", "dumbbells", "beginner"),
    ("Plank", "isolation", "core", "bodyweight", "beginner"),
    ("Romanian Deadlift", "compound", "hamstrings", "barbell", "intermediate"),
    ("Incline Dumbbell Press", "compound", "chest", "dumbbells, bench", "intermediate"),
    ("Seated Cable Row", "compound", "back", "cable machine", "beginner"),
    ("Treadmill Run", "cardio", "cardiovascular", "treadmill", "beginner"),
    ("Jump Rope", "cardio", "cardiovascular", "jump rope", "beginner"),
]


async def seed_exercises(db):
    for name, category, muscle, equipment, difficulty in EXERCISES:
        exercise = Exercise(
            name=name,
            category=category,
            primary_muscle=muscle,
            equipment_needed=equipment,
            difficulty=difficulty,
        )
        db.add(exercise)
    await db.commit()
    print(f"Seeded {len(EXERCISES)} exercises.")


async def seed_admin(db):
    admin = User(
        email="admin@fitmentor.ai",
        hashed_password=hash_password("ChangeMe123!"),
        full_name="FitMentor Admin",
        auth_provider=AuthProvider.EMAIL,
        is_admin=True,
        is_onboarded=True,
    )
    db.add(admin)
    await db.commit()
    print("Seeded admin user: admin@fitmentor.ai / ChangeMe123! (CHANGE THIS PASSWORD IMMEDIATELY)")


async def main():
    async with AsyncSessionLocal() as db:
        await seed_exercises(db)
        await seed_admin(db)


if __name__ == "__main__":
    asyncio.run(main())
