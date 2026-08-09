"use client";

import { useState } from "react";
import Link from "next/link";
import { useLogin } from "@/hooks/useAuth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate({ email, password });
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <div className="glass-panel w-full max-w-md p-8">
        <h1 className="font-display font-bold text-2xl mb-1">Welcome back</h1>
        <p className="text-mute text-sm mb-8">Your coach picked up right where you left off.</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            required
            placeholder="Email"
            className="input-field"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            required
            placeholder="Password"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {login.isError && (
            <p className="text-ember-400 text-sm">
              Incorrect email or password. Try again.
            </p>
          )}

          <button type="submit" disabled={login.isPending} className="btn-primary mt-2 disabled:opacity-60">
            {login.isPending ? "Logging in…" : "Log in"}
          </button>
        </form>

        <p className="text-mute text-sm text-center mt-6">
          New here?{" "}
          <Link href="/register" className="text-ember-400 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}
