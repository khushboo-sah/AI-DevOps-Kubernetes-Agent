"use client";

import { FormEvent, useState } from "react";

import { useAuthSession } from "@/hooks/useAuthSession";

export function AuthPanel() {
  const { authMessage, signIn, signUp, verifyEmail } = useAuthSession();
  const [mode, setMode] = useState<"sign-in" | "sign-up" | "verify">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (mode === "sign-in") {
        await signIn(email, password);
      } else if (mode === "sign-up") {
        await signUp(email, password, name || undefined);
        setMode("verify");
      } else {
        await verifyEmail(email, otp);
      }
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Authentication failed",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-600">
          AI Kubernetes Agent
        </p>
        <h1 className="mt-3 text-3xl font-bold text-slate-950">
          {mode === "sign-in" ? "Login" : mode === "sign-up" ? "Create account" : "Verify email"}
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Sign in with InsForge to investigate clusters and view diagnosis history.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {mode === "sign-up" ? (
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Name</span>
              <input
                className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                onChange={(event) => setName(event.target.value)}
                placeholder="Khushboo"
                value={name}
              />
            </label>
          ) : null}

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
              type="email"
              value={email}
            />
          </label>

          {mode === "verify" ? (
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Verification code</span>
              <input
                className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                onChange={(event) => setOtp(event.target.value)}
                placeholder="123456"
                required
                value={otp}
              />
            </label>
          ) : (
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Password</span>
              <input
                className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                onChange={(event) => setPassword(event.target.value)}
                required
                type="password"
                value={password}
              />
            </label>
          )}

          {authMessage ? (
            <p className="rounded-xl bg-blue-50 px-3 py-2 text-sm text-blue-700">
              {authMessage}
            </p>
          ) : null}
          {error ? (
            <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : null}

          <button
            className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting
              ? "Please wait..."
              : mode === "sign-in"
                ? "Login"
                : mode === "sign-up"
                  ? "Sign up"
                  : "Verify email"}
          </button>
        </form>

        <div className="mt-5 flex justify-center gap-4 text-sm">
          <button
            className="font-medium text-blue-600 hover:text-blue-700"
            onClick={() => setMode(mode === "sign-in" ? "sign-up" : "sign-in")}
            type="button"
          >
            {mode === "sign-in" ? "Create an account" : "Back to login"}
          </button>
          {mode !== "verify" ? (
            <button
              className="font-medium text-slate-500 hover:text-slate-700"
              onClick={() => setMode("verify")}
              type="button"
            >
              Verify code
            </button>
          ) : null}
        </div>
      </section>
    </main>
  );
}
