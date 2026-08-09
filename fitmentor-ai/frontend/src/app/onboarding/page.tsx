"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCompleteOnboarding } from "@/hooks/useFitness";

const STEPS = ["Basics", "Goal", "Health", "Diet", "Training", "Lifestyle", "Preferences"];

const initialForm = {
  age: "", gender: "male", height_cm: "", weight_kg: "", target_weight_kg: "", body_fat_percent: "",
  fitness_goal: "build_muscle", fitness_level: "beginner", experience: "never",
  medical_conditions: "", past_injuries: "", medications: "", allergies: "",
  diet_type: "non_vegetarian", food_allergies: "", preferred_cuisine: "", daily_budget: "",
  workout_location: "gym", gym_equipment: "", workout_time: "morning", workout_days: "4", workout_duration_minutes: "60",
  sleep_time: "23:00", wake_time: "07:00", stress_level: "moderate", water_intake_liters: "2.5",
  occupation: "", activity_level: "moderately_active", smoking: false, alcohol: false, daily_step_count: "",
  favorite_exercises: "", disliked_exercises: "", target_muscles: "", weak_muscles: "", strong_muscles: "",
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(initialForm);
  const complete = useCompleteOnboarding();

  const update = (key: keyof typeof form, value: string | boolean) =>
    setForm((f) => ({ ...f, [key]: value }));

  const isLast = step === STEPS.length - 1;

  const [stepError, setStepError] = useState<string | null>(null);

  const validateStep = (): string | null => {
    if (step === 0) {
      if (!form.age || Number(form.age) < 13) return "Enter a valid age (13+).";
      if (!form.height_cm || Number(form.height_cm) <= 0) return "Enter your height.";
      if (!form.weight_kg || Number(form.weight_kg) <= 0) return "Enter your weight.";
      if (!form.target_weight_kg || Number(form.target_weight_kg) <= 0) return "Enter your target weight.";
    }
    if (step === 4) {
      if (!form.workout_days || Number(form.workout_days) < 1 || Number(form.workout_days) > 7) return "Workout days must be between 1 and 7.";
      if (!form.workout_duration_minutes || Number(form.workout_duration_minutes) < 10) return "Session duration must be at least 10 minutes.";
    }
    return null;
  };

  const handleNext = () => {
    const err = validateStep();
    if (err) {
      setStepError(err);
      return;
    }
    setStepError(null);

    if (isLast) {
      const payload = {
        ...form,
        age: Number(form.age),
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        target_weight_kg: Number(form.target_weight_kg),
        body_fat_percent: form.body_fat_percent ? Number(form.body_fat_percent) : undefined,
        daily_budget: form.daily_budget ? Number(form.daily_budget) : undefined,
        workout_days: Number(form.workout_days),
        workout_duration_minutes: Number(form.workout_duration_minutes),
        water_intake_liters: form.water_intake_liters ? Number(form.water_intake_liters) : undefined,
        daily_step_count: form.daily_step_count ? Number(form.daily_step_count) : undefined,
      };
      complete.mutate(payload, { onSuccess: () => router.push("/dashboard") });
    } else {
      setStep((s) => s + 1);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="glass-panel w-full max-w-2xl p-8">
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((label, i) => (
            <div key={label} className={`h-1 flex-1 rounded-full ${i <= step ? "bg-ember-500" : "bg-white/10"}`} />
          ))}
        </div>
        <p className="ai-badge mb-1">Step {step + 1} of {STEPS.length}</p>
        <h1 className="font-display font-bold text-2xl mb-6">{STEPS[step]}</h1>

        <div className="flex flex-col gap-4">
          {step === 0 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <input className="input-field" type="number" placeholder="Age" value={form.age} onChange={(e) => update("age", e.target.value)} />
                <select className="input-field" value={form.gender} onChange={(e) => update("gender", e.target.value)}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <input className="input-field" type="number" placeholder="Height (cm)" value={form.height_cm} onChange={(e) => update("height_cm", e.target.value)} />
                <input className="input-field" type="number" placeholder="Weight (kg)" value={form.weight_kg} onChange={(e) => update("weight_kg", e.target.value)} />
                <input className="input-field" type="number" placeholder="Target weight (kg)" value={form.target_weight_kg} onChange={(e) => update("target_weight_kg", e.target.value)} />
              </div>
              <input className="input-field" type="number" placeholder="Body fat % (optional)" value={form.body_fat_percent} onChange={(e) => update("body_fat_percent", e.target.value)} />
            </>
          )}

          {step === 1 && (
            <>
              <select className="input-field" value={form.fitness_goal} onChange={(e) => update("fitness_goal", e.target.value)}>
                {["lose_fat", "build_muscle", "recomposition", "weight_gain", "athletic_performance", "powerlifting", "bodybuilding", "general_fitness"].map((g) => (
                  <option key={g} value={g}>{g.replace(/_/g, " ")}</option>
                ))}
              </select>
              <select className="input-field" value={form.fitness_level} onChange={(e) => update("fitness_level", e.target.value)}>
                {["beginner", "intermediate", "advanced"].map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
              <select className="input-field" value={form.experience} onChange={(e) => update("experience", e.target.value)}>
                {["never", "<1y", "1-3y", "3-5y", "5y+"].map((x) => <option key={x} value={x}>{x}</option>)}
              </select>
            </>
          )}

          {step === 2 && (
            <>
              <input className="input-field" placeholder="Medical conditions (or 'none')" value={form.medical_conditions} onChange={(e) => update("medical_conditions", e.target.value)} />
              <input className="input-field" placeholder="Past injuries (or 'none')" value={form.past_injuries} onChange={(e) => update("past_injuries", e.target.value)} />
              <input className="input-field" placeholder="Medications (or 'none')" value={form.medications} onChange={(e) => update("medications", e.target.value)} />
              <input className="input-field" placeholder="Allergies (or 'none')" value={form.allergies} onChange={(e) => update("allergies", e.target.value)} />
            </>
          )}

          {step === 3 && (
            <>
              <select className="input-field" value={form.diet_type} onChange={(e) => update("diet_type", e.target.value)}>
                {["vegetarian", "vegan", "non_vegetarian", "eggetarian"].map((d) => <option key={d} value={d}>{d.replace("_", "-")}</option>)}
              </select>
              <input className="input-field" placeholder="Food allergies" value={form.food_allergies} onChange={(e) => update("food_allergies", e.target.value)} />
              <input className="input-field" placeholder="Preferred cuisine" value={form.preferred_cuisine} onChange={(e) => update("preferred_cuisine", e.target.value)} />
              <input className="input-field" type="number" placeholder="Daily food budget (optional)" value={form.daily_budget} onChange={(e) => update("daily_budget", e.target.value)} />
            </>
          )}

          {step === 4 && (
            <>
              <select className="input-field" value={form.workout_location} onChange={(e) => update("workout_location", e.target.value)}>
                {["home", "gym", "hybrid"].map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
              <input className="input-field" placeholder="Gym equipment available" value={form.gym_equipment} onChange={(e) => update("gym_equipment", e.target.value)} />
              <div className="grid grid-cols-2 gap-4">
                <input className="input-field" type="number" placeholder="Workout days/week" value={form.workout_days} onChange={(e) => update("workout_days", e.target.value)} />
                <input className="input-field" type="number" placeholder="Session duration (min)" value={form.workout_duration_minutes} onChange={(e) => update("workout_duration_minutes", e.target.value)} />
              </div>
            </>
          )}

          {step === 5 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <input className="input-field" type="time" value={form.sleep_time} onChange={(e) => update("sleep_time", e.target.value)} />
                <input className="input-field" type="time" value={form.wake_time} onChange={(e) => update("wake_time", e.target.value)} />
              </div>
              <select className="input-field" value={form.stress_level} onChange={(e) => update("stress_level", e.target.value)}>
                {["low", "moderate", "high", "very_high"].map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
              </select>
              <select className="input-field" value={form.activity_level} onChange={(e) => update("activity_level", e.target.value)}>
                {["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"].map((a) => <option key={a} value={a}>{a.replace(/_/g, " ")}</option>)}
              </select>
              <input className="input-field" placeholder="Occupation" value={form.occupation} onChange={(e) => update("occupation", e.target.value)} />
              <div className="flex gap-6 items-center px-1">
                <label className="flex items-center gap-2 text-sm text-mute">
                  <input type="checkbox" checked={form.smoking} onChange={(e) => update("smoking", e.target.checked)} /> Smoking
                </label>
                <label className="flex items-center gap-2 text-sm text-mute">
                  <input type="checkbox" checked={form.alcohol} onChange={(e) => update("alcohol", e.target.checked)} /> Alcohol
                </label>
              </div>
            </>
          )}

          {step === 6 && (
            <>
              <input className="input-field" placeholder="Favorite exercises" value={form.favorite_exercises} onChange={(e) => update("favorite_exercises", e.target.value)} />
              <input className="input-field" placeholder="Exercises you hate" value={form.disliked_exercises} onChange={(e) => update("disliked_exercises", e.target.value)} />
              <input className="input-field" placeholder="Target muscles" value={form.target_muscles} onChange={(e) => update("target_muscles", e.target.value)} />
              <input className="input-field" placeholder="Weak muscles" value={form.weak_muscles} onChange={(e) => update("weak_muscles", e.target.value)} />
              <input className="input-field" placeholder="Strong muscles" value={form.strong_muscles} onChange={(e) => update("strong_muscles", e.target.value)} />
            </>
          )}
        </div>

        {stepError && <p className="text-ember-400 text-sm mt-2">{stepError}</p>}

        {complete.isError && (
          <p className="text-ember-400 text-sm mt-4">
            {(() => {
              const detail = (complete.error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
              if (Array.isArray(detail)) {
                return detail
                  .map((d: { loc?: (string | number)[]; msg?: string }) => `${d.loc?.[d.loc.length - 1]}: ${d.msg}`)
                  .join(" · ");
              }
              if (typeof detail === "string") return detail;
              return "Something went wrong saving your profile. Please check every step has a value and try again.";
            })()}
          </p>
        )}

        <div className="flex justify-between mt-8">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="btn-secondary disabled:opacity-30"
          >
            Back
          </button>
          <button onClick={handleNext} disabled={complete.isPending} className="btn-primary disabled:opacity-60">
            {isLast ? (complete.isPending ? "Analyzing your profile…" : "Finish & build my plan") : "Next"}
          </button>
        </div>
      </div>
    </main>
  );
}