"use client";

import { useState } from "react";
import { useSubmitCheckIn } from "@/hooks/useFitness";

const initial = {
  weight_kg: "", sleep_hours: "", energy_level: 5, mood: 5, soreness: 3, stress: 3,
  water_liters: "", calories_yesterday: "", workout_completed: false, steps: "",
};

function SliderField({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-mute">{label}</span>
        <span className="text-bone font-mono">{value}</span>
      </div>
      <input type="range" min={1} max={10} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-ember-500" />
    </div>
  );
}

export default function CheckInPage() {
  const [form, setForm] = useState(initial);
  const submit = useSubmitCheckIn();

  const update = (key: keyof typeof form, value: string | number | boolean) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = () => {
    submit.mutate({
      weight_kg: form.weight_kg ? Number(form.weight_kg) : undefined,
      sleep_hours: form.sleep_hours ? Number(form.sleep_hours) : undefined,
      energy_level: form.energy_level,
      mood: form.mood,
      soreness: form.soreness,
      stress: form.stress,
      water_liters: form.water_liters ? Number(form.water_liters) : undefined,
      calories_yesterday: form.calories_yesterday ? Number(form.calories_yesterday) : undefined,
      workout_completed: form.workout_completed,
      steps: form.steps ? Number(form.steps) : undefined,
    });
  };

  return (
    <div>
      <h1 className="font-display font-bold text-3xl">Daily check-in</h1>
      <p className="text-mute mt-2">Two minutes now sharpens everything your coach adjusts today.</p>

      <div className="glass-panel p-6 mt-6 flex flex-col gap-6 max-w-lg">
        <div className="grid grid-cols-2 gap-4">
          <input className="input-field" type="number" placeholder="Weight (kg)" value={form.weight_kg} onChange={(e) => update("weight_kg", e.target.value)} />
          <input className="input-field" type="number" placeholder="Sleep hours" value={form.sleep_hours} onChange={(e) => update("sleep_hours", e.target.value)} />
        </div>

        <SliderField label="Energy" value={form.energy_level} onChange={(v) => update("energy_level", v)} />
        <SliderField label="Mood" value={form.mood} onChange={(v) => update("mood", v)} />
        <SliderField label="Soreness" value={form.soreness} onChange={(v) => update("soreness", v)} />
        <SliderField label="Stress" value={form.stress} onChange={(v) => update("stress", v)} />

        <div className="grid grid-cols-2 gap-4">
          <input className="input-field" type="number" placeholder="Water (L)" value={form.water_liters} onChange={(e) => update("water_liters", e.target.value)} />
          <input className="input-field" type="number" placeholder="Calories yesterday" value={form.calories_yesterday} onChange={(e) => update("calories_yesterday", e.target.value)} />
        </div>
        <input className="input-field" type="number" placeholder="Steps" value={form.steps} onChange={(e) => update("steps", e.target.value)} />

        <label className="flex items-center gap-2 text-sm text-mute">
          <input type="checkbox" checked={form.workout_completed} onChange={(e) => update("workout_completed", e.target.checked)} />
          I completed my workout
        </label>

        {submit.isSuccess && <p className="text-signal-400 text-sm">Logged — your coach has this now.</p>}
        {submit.isError && <p className="text-ember-400 text-sm">Something went wrong. Try again.</p>}

        <button onClick={handleSubmit} disabled={submit.isPending} className="btn-primary disabled:opacity-60">
          {submit.isPending ? "Saving…" : "Submit check-in"}
        </button>
      </div>
    </div>
  );
}
