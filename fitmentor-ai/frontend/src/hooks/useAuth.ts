import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export function useLogin() {
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);

  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<TokenPair>("/auth/login", payload);
      return data;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      router.push("/dashboard");
    },
  });
}

export function useRegister() {
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);

  return useMutation({
    mutationFn: async (payload: { email: string; password: string; full_name: string }) => {
      const { data } = await api.post<TokenPair>("/auth/register", payload);
      return data;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      router.push("/onboarding");
    },
  });
}
