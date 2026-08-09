import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

// ---------- Onboarding / Scores ----------
export const useLatestScores = () =>
  useQuery({
    queryKey: ["scores", "latest"],
    queryFn: async () => (await api.get("/onboarding/scores/latest")).data,
    retry: false,
  });

export const useCompleteOnboarding = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      (await api.post("/onboarding/complete", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scores"] }),
  });
};

// ---------- Workouts ----------
export const useActiveWorkoutPlan = () =>
  useQuery({
    queryKey: ["workouts", "active"],
    queryFn: async () => (await api.get("/workouts/active")).data,
    retry: false,
  });

export const useGenerateWorkoutPlan = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { week_number?: number; is_deload_week?: boolean } = {}) =>
      (await api.post("/workouts/generate", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workouts"] }),
  });
};

export const useLogWorkoutSession = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      (await api.post("/workouts/sessions", payload)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workouts", "sessions"] });
      qc.invalidateQueries({ queryKey: ["gamification"] });
    },
  });
};

export const useWorkoutSessions = () =>
  useQuery({
    queryKey: ["workouts", "sessions"],
    queryFn: async () => (await api.get("/workouts/sessions")).data,
  });

// ---------- Nutrition ----------
export const useActiveNutritionPlan = () =>
  useQuery({
    queryKey: ["nutrition", "active"],
    queryFn: async () => (await api.get("/nutrition/active")).data,
    retry: false,
  });

export const useGenerateNutritionPlan = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await api.post("/nutrition/generate")).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["nutrition"] }),
  });
};

// ---------- Chat coach ----------
export const useChatHistory = () =>
  useQuery({
    queryKey: ["chat", "history"],
    queryFn: async () => (await api.get("/coach/chat/history")).data,
  });

export const useSendChatMessage = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (message: string) => (await api.post("/coach/chat/send", { message })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chat", "history"] }),
  });
};

// ---------- Daily check-in ----------
export const useSubmitCheckIn = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      (await api.post("/checkins/today", payload)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["checkins"] });
      qc.invalidateQueries({ queryKey: ["gamification"] });
      qc.invalidateQueries({ queryKey: ["progress"] });
    },
  });
};

export const useCheckInHistory = (days = 30) =>
  useQuery({
    queryKey: ["checkins", "history", days],
    queryFn: async () => (await api.get(`/checkins/history?days=${days}`)).data,
  });

// ---------- Progress ----------
export const useProgressEntries = (days = 90) =>
  useQuery({
    queryKey: ["progress", "entries", days],
    queryFn: async () => (await api.get(`/progress/entries?days=${days}`)).data,
  });

export const useWeeklyReview = () =>
  useQuery({
    queryKey: ["progress", "weekly-review"],
    queryFn: async () => (await api.get("/progress/weekly-review")).data,
  });

// ---------- Gamification ----------
export const useGamificationProfile = () =>
  useQuery({
    queryKey: ["gamification"],
    queryFn: async () => (await api.get("/gamification/me")).data,
  });

// ---------- Notifications ----------
export const useNotifications = () =>
  useQuery({
    queryKey: ["notifications"],
    queryFn: async () => (await api.get("/notifications")).data,
  });
