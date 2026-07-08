"use client";

import { AuthPanel } from "@/components/AuthPanel";
import { Dashboard } from "@/components/Dashboard";
import { useAuthSession } from "@/hooks/useAuthSession";

export default function HomePage() {
  const { isLoading, user } = useAuthSession();

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
        <div className="rounded-2xl border border-slate-200 bg-white px-6 py-4 text-sm font-medium text-slate-600 shadow-sm">
          Loading AI Kubernetes Agent...
        </div>
      </main>
    );
  }

  if (!user) {
    return <AuthPanel />;
  }

  return <Dashboard />;
}
