"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Flame, Trophy, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { useGamificationProfile, useLatestScores } from "@/hooks/useFitness";

interface Me {
  full_name: string;
  is_onboarded: boolean;
}

const SCORE_LABELS: Record<string, string> = {
  fitness_score: "Fitness",
  health_score: "Health",
  muscle_balance_score: "Muscle Balance",
  lifestyle_score: "Lifestyle",
  recovery_score: "Recovery",
};

export default function DashboardOverviewPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [me, setMe] = useState<Me | null>(null);

  const { data: scores, isLoading: scoresLoading } = useLatestScores();
  const { data: gamification } = useGamificationProfile();

  useEffect(() => {
    if (!accessToken) {
      router.push("/login");
      return;
    }
    api.get<Me>("/auth/me").then((res) => {
      setMe(res.data);
      if (!res.data.is_onboarded) router.push("/onboarding");
    });
  }, [accessToken, router]);

  if (!me) {
    return <p className="text-mute">Loading your dashboard…</p>;
  }

  return (
    <div>
      <h1 className="font-display font-bold text-3xl">Welcome back, {me.full_name.split(" ")[0]}</h1>
      <p className="text-mute mt-2">Here's where you stand today.</p>

      {gamification && (
        <div className="glass-panel p-5 mt-6 flex items-center gap-8">
          <div className="flex items-center gap-2">
            <Zap className="text-ember-500" size={20} />
            <span className="font-display font-bold text-lg">{gamification.xp} XP</span>
            <span className="text-mute text-sm">· Level {gamification.level}</span>
          </div>
          <div className="flex items-center gap-2">
            <Flame className="text-ember-500" size={20} />
            <span className="text-sm">{gamification.current_streak_days} day streak</span>
          </div>
          <div className="flex items-center gap-2">
            <Trophy className="text-signal-400" size={20} />
            <span className="text-sm">{gamification.badges?.length ?? 0} badges</span>
          </div>
        </div>
      )}

      <section className="mt-8">
        <span className="ai-badge">Your AI analysis</span>
        {scoresLoading && <p className="text-mute mt-2">Loading scores…</p>}
        {!scoresLoading && !scores && (
          <p className="text-mute mt-2">Scores will appear once onboarding finishes analyzing your profile.</p>
        )}
        {scores && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-3">
            {Object.entries(SCORE_LABELS).map(([key, label]) => (
              <div key={key} className="glass-panel p-4">
                <p className="text-mute text-xs mb-1">{label}</p>
                <p className="font-display font-bold text-2xl">{scores[key]}</p>
              </div>
            ))}
          </div>
        )}
        {scores?.explanations && (
          <div className="glass-panel p-5 mt-4 flex flex-col gap-3">
            {Object.entries(SCORE_LABELS).map(([key, label]) => (
              <p key={key} className="text-sm text-mute">
                <span className="text-bone font-medium">{label}:</span> {scores.explanations[key]}
              </p>
            ))}
          </div>
        )}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-10">
        <Link href="/dashboard/workouts" className="glass-panel p-6 hover:border-ember-500/40 border border-transparent transition-colors">
          <h3 className="font-display font-semibold text-lg mb-1">Workout Plan</h3>
          <p className="text-mute text-sm">Generate or view your AI-built training split.</p>
        </Link>
        <Link href="/dashboard/nutrition" className="glass-panel p-6 hover:border-ember-500/40 border border-transparent transition-colors">
          <h3 className="font-display font-semibold text-lg mb-1">Nutrition Plan</h3>
          <p className="text-mute text-sm">Your calories, macros, and meal plan.</p>
        </Link>
        <Link href="/dashboard/coach" className="glass-panel p-6 hover:border-ember-500/40 border border-transparent transition-colors">
          <h3 className="font-display font-semibold text-lg mb-1">AI Coach Chat</h3>
          <p className="text-mute text-sm">Ask anything — form checks, swaps, motivation.</p>
        </Link>
        <Link href="/dashboard/progress" className="glass-panel p-6 hover:border-ember-500/40 border border-transparent transition-colors">
          <h3 className="font-display font-semibold text-lg mb-1">Progress &amp; Weekly Review</h3>
          <p className="text-mute text-sm">Weight trend, adherence, and this week's suggestions.</p>
        </Link>
      </section>
    </div>
  );
}
