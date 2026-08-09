"use client";

import { useActiveNutritionPlan, useGenerateNutritionPlan } from "@/hooks/useFitness";

interface MealItem {
  item: string;
  portion: string;
  calories: number;
  protein_g: number;
}

const MEAL_LABELS: Record<string, string> = {
  breakfast: "Breakfast",
  lunch: "Lunch",
  dinner: "Dinner",
  snacks: "Snacks",
  pre_workout: "Pre-workout",
  post_workout: "Post-workout",
};

export default function NutritionPage() {
  const { data: plan, isLoading, isError } = useActiveNutritionPlan();
  const generate = useGenerateNutritionPlan();

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display font-bold text-3xl">Nutrition Plan</h1>
        <button onClick={() => generate.mutate()} disabled={generate.isPending} className="btn-primary disabled:opacity-60">
          {generate.isPending ? "Building your plan…" : plan ? "Regenerate plan" : "Generate plan"}
        </button>
      </div>

      {isLoading && <p className="text-mute mt-6">Loading…</p>}
      {isError && !plan && <p className="text-mute mt-6">No active plan yet — generate one to get started.</p>}
      {generate.isError && <p className="text-ember-400 mt-4 text-sm">Couldn't generate a plan right now. Please try again.</p>}

      {plan && (
        <div className="mt-6">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            {[
              ["Calories", plan.daily_calories],
              ["Protein", `${plan.protein_g}g`],
              ["Carbs", `${plan.carbs_g}g`],
              ["Fat", `${plan.fat_g}g`],
              ["Fiber", `${plan.fiber_g}g`],
              ["Water", `${plan.water_liters}L`],
            ].map(([label, value]) => (
              <div key={label as string} className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">{label}</p>
                <p className="font-display font-bold text-xl">{value}</p>
              </div>
            ))}
          </div>

          <div className="glass-panel p-5 mt-4">
            <p className="text-bone text-sm">{plan.ai_rationale}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {Object.entries(plan.meal_plan?.meals ?? {}).map(([slot, items]) => (
              <div key={slot} className="glass-panel p-5">
                <h3 className="font-display font-semibold mb-3">{MEAL_LABELS[slot] ?? slot}</h3>
                <div className="flex flex-col gap-2">
                  {(items as MealItem[]).map((item, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-bone">{item.item} <span className="text-mute">({item.portion})</span></span>
                      <span className="text-mute font-mono text-xs">{item.calories} kcal</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {plan.grocery_list && (
            <div className="glass-panel p-5 mt-6">
              <h3 className="font-display font-semibold mb-3">Shopping list</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(plan.grocery_list).map(([category, items]) => (
                  <div key={category}>
                    <p className="ai-badge mb-2">{category}</p>
                    <ul className="text-sm text-mute flex flex-col gap-1">
                      {(items as string[]).map((item) => <li key={item}>{item}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
