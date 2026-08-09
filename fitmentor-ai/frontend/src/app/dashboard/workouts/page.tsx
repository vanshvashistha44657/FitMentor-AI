"use client";

import { useActiveWorkoutPlan, useGenerateWorkoutPlan, useLogWorkoutSession } from "@/hooks/useFitness";

interface Exercise {
  name: string;
  category: string;
  sets: number;
  reps: string;
  tempo: string;
  rest_seconds: number;
  target_rpe: number;
  notes?: string;
}

interface WorkoutDay {
  day_label: string;
  focus: string;
  exercises: Exercise[];
}

export default function WorkoutsPage() {
  const { data: plan, isLoading, isError } = useActiveWorkoutPlan();
  const generate = useGenerateWorkoutPlan();
  const logSession = useLogWorkoutSession();

  const handleLogDay = (day: WorkoutDay) => {
    logSession.mutate({
      plan_id: plan?.id,
      day_label: day.day_label,
      completed: true,
      sets: day.exercises.map((ex) => ({ exercise: ex.name })),
    });
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display font-bold text-3xl">Workout Plan</h1>
        <button onClick={() => generate.mutate({})} disabled={generate.isPending} className="btn-primary disabled:opacity-60">
          {generate.isPending ? "Building your program…" : plan ? "Regenerate plan" : "Generate plan"}
        </button>
      </div>

      {isLoading && <p className="text-mute mt-6">Loading…</p>}
      {isError && !plan && <p className="text-mute mt-6">No active plan yet — generate one to get started.</p>}
      {generate.isError && <p className="text-ember-400 mt-4 text-sm">Couldn't generate a plan right now. Please try again.</p>}

      {plan && (
        <div className="mt-6">
          <div className="glass-panel p-5">
            <span className="ai-badge">{plan.split_type} · Week {plan.week_number}{plan.is_deload_week ? " · Deload" : ""}</span>
            <p className="text-bone mt-2 text-sm">{plan.ai_rationale}</p>
          </div>

          <div className="grid grid-cols-1 gap-4 mt-6">
            {plan.plan_data?.days?.map((day: WorkoutDay) => (
              <div key={day.day_label} className="glass-panel p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-display font-semibold text-lg">{day.day_label}</h3>
                    <p className="text-mute text-sm">{day.focus}</p>
                  </div>
                  <button onClick={() => handleLogDay(day)} className="btn-secondary text-sm px-4 py-2">
                    Mark completed
                  </button>
                </div>

                <div className="mt-4 flex flex-col gap-2">
                  {day.exercises.map((ex) => (
                    <div key={ex.name} className="flex items-center justify-between text-sm py-2 border-b border-white/5 last:border-0">
                      <span className="text-bone">{ex.name}</span>
                      <span className="text-mute font-mono text-xs">
                        {ex.sets}×{ex.reps} · RPE {ex.target_rpe} · rest {ex.rest_seconds}s
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
