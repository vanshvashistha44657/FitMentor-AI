"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_onboarded: boolean;
  subscription_tier: string;
}

interface Analytics {
  total_users: number;
  onboarded_users: number;
  onboarding_rate_percent: number;
  total_workout_plans: number;
  total_workout_sessions: number;
  total_nutrition_plans: number;
  total_chat_messages: number;
}

export default function AdminPage() {
  const qc = useQueryClient();

  const { data: analytics } = useQuery<Analytics>({
    queryKey: ["admin", "analytics"],
    queryFn: async () => (await api.get("/admin/analytics")).data,
  });

  const { data: users } = useQuery<AdminUser[]>({
    queryKey: ["admin", "users"],
    queryFn: async () => (await api.get("/admin/users")).data,
  });

  const toggleActive = useMutation({
    mutationFn: async ({ id, activate }: { id: string; activate: boolean }) =>
      api.post(`/admin/users/${id}/${activate ? "reactivate" : "deactivate"}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "users"] }),
  });

  return (
    <main className="min-h-screen px-10 py-10 max-w-6xl mx-auto">
      <h1 className="font-display font-bold text-3xl mb-8">Admin Dashboard</h1>

      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {[
            ["Total users", analytics.total_users],
            ["Onboarded", `${analytics.onboarding_rate_percent}%`],
            ["Workout plans", analytics.total_workout_plans],
            ["Nutrition plans", analytics.total_nutrition_plans],
            ["Workout sessions", analytics.total_workout_sessions],
            ["Chat messages", analytics.total_chat_messages],
          ].map(([label, value]) => (
            <div key={label as string} className="glass-panel p-4">
              <p className="text-mute text-xs mb-1">{label}</p>
              <p className="font-display font-bold text-2xl">{value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="glass-panel p-5">
        <h3 className="font-display font-semibold mb-4">Users</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-mute text-left border-b border-white/10">
              <th className="pb-2">Name</th>
              <th className="pb-2">Email</th>
              <th className="pb-2">Tier</th>
              <th className="pb-2">Onboarded</th>
              <th className="pb-2">Status</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {users?.map((u) => (
              <tr key={u.id} className="border-b border-white/5">
                <td className="py-2">{u.full_name}</td>
                <td className="py-2 text-mute">{u.email}</td>
                <td className="py-2 text-mute">{u.subscription_tier}</td>
                <td className="py-2 text-mute">{u.is_onboarded ? "Yes" : "No"}</td>
                <td className="py-2">
                  <span className={u.is_active ? "text-signal-400" : "text-ember-400"}>
                    {u.is_active ? "Active" : "Deactivated"}
                  </span>
                </td>
                <td className="py-2">
                  <button
                    onClick={() => toggleActive.mutate({ id: u.id, activate: !u.is_active })}
                    className="text-xs text-mute hover:text-bone underline"
                  >
                    {u.is_active ? "Deactivate" : "Reactivate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
