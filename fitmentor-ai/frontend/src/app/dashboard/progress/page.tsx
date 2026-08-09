"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useProgressEntries, useWeeklyReview } from "@/hooks/useFitness";

interface ProgressEntry {
  entry_date: string;
  weight_kg: number | null;
}

export default function ProgressPage() {
  const { data: entries } = useProgressEntries();
  const { data: review, isLoading: reviewLoading } = useWeeklyReview();

  const chartData = (entries ?? [])
    .filter((e: ProgressEntry) => e.weight_kg !== null)
    .map((e: ProgressEntry) => ({ date: e.entry_date.slice(5), weight: e.weight_kg }));

  return (
    <div>
      <h1 className="font-display font-bold text-3xl">Progress &amp; Weekly Review</h1>
      <p className="text-mute mt-2">Your trend, not just today's snapshot.</p>

      <div className="glass-panel p-6 mt-6">
        <h3 className="font-display font-semibold mb-4">Weight trend</h3>
        {chartData.length < 2 ? (
          <p className="text-mute text-sm">Log a couple more check-ins to see your trend line.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232830" />
              <XAxis dataKey="date" stroke="#8A8F98" fontSize={12} />
              <YAxis stroke="#8A8F98" fontSize={12} domain={["auto", "auto"]} />
              <Tooltip contentStyle={{ background: "#181C22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12 }} />
              <Line type="monotone" dataKey="weight" stroke="#FF6B2C" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="mt-8">
        <span className="ai-badge">This week</span>
        {reviewLoading && <p className="text-mute mt-2">Loading review…</p>}
        {review && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
              <div className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">Adherence</p>
                <p className="font-display font-bold text-2xl">{review.adherence_percent}%</p>
              </div>
              <div className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">Workout score</p>
                <p className="font-display font-bold text-2xl">{review.workout_score}%</p>
              </div>
              <div className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">Workouts done</p>
                <p className="font-display font-bold text-2xl">{review.workouts_completed}</p>
              </div>
              <div className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">Avg sleep</p>
                <p className="font-display font-bold text-2xl">{review.avg_sleep_hours ?? "—"}h</p>
              </div>
            </div>

            <div className="glass-panel p-5 mt-4">
              <h3 className="font-display font-semibold mb-3">Coach's suggestions</h3>
              <ul className="flex flex-col gap-2">
                {review.suggestions.map((s: string, i: number) => (
                  <li key={i} className="text-sm text-bone flex gap-2">
                    <span className="text-ember-500">→</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
