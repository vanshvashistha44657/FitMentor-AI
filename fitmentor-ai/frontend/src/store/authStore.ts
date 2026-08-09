import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  isOnboarded: boolean;
  setTokens: (access: string, refresh: string) => void;
  setOnboarded: (value: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      isOnboarded: false,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setOnboarded: (value) => set({ isOnboarded: value }),
      logout: () => set({ accessToken: null, refreshToken: null, isOnboarded: false }),
    }),
    { name: "fitmentor-auth" }
  )
);
