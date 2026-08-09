"use client";

import { useState } from "react";
import Link from "next/link";
import { useRegister } from "@/hooks/useAuth";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const register = useRegister();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register.mutate({ email, password, full_name: fullName });
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <div className="glass-panel w-full max-w-md p-8">
        <h1 className="font-display font-bold text-2xl mb-1">Build your plan</h1>
        <p className="text-mute text-sm mb-8">
          Two minutes of setup, then a plan built entirely around you.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            required
            placeholder="Full name"
            className="input-field"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
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
            minLength={8}
            placeholder="Password (min. 8 characters)"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {register.isError && (
            <p className="text-ember-400 text-sm">
              Something went wrong — that email may already be registered.
            </p>
          )}

          <button type="submit" disabled={register.isPending} className="btn-primary mt-2 disabled:opacity-60">
            {register.isPending ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-mute text-sm text-center mt-6">
          Already training with us?{" "}
          <Link href="/login" className="text-ember-400 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
