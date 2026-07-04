"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { DiagnosisCard } from "@/components/DiagnosisCard";
import { HistoryTable } from "@/components/HistoryTable";
import { ProgressList } from "@/components/ProgressList";
import { useAuthSession } from "@/hooks/useAuthSession";
import { useInvestigationProgress } from "@/hooks/useInvestigationProgress";
import {
  fetchInvestigationHistory,
  runInvestigation,
  saveInvestigationHistory,
} from "@/services/investigations";
import { Diagnosis } from "@/types/investigation";

const PROGRESS_SEQUENCE = [
  "pods",
  "logs",
  "events",
  "deployments",
  "network",
  "ai",
  "root-cause",
];

export function Dashboard() {
  const { accessToken, signOut, user } = useAuthSession();
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const { isRealtimeReady, publishProgress, resetProgress, steps } =
    useInvestigationProgress(user?.id);

  const historyQuery = useQuery({
    queryKey: ["investigation-history", user?.id],
    queryFn: () => fetchInvestigationHistory(user?.id ?? ""),
    enabled: Boolean(user?.id),
  });

  async function handleInvestigate() {
    if (!user || !accessToken) {
      setError("Please login before starting an investigation.");
      return;
    }

    setDiagnosis(null);
    setError(null);
    setIsInvestigating(true);
    resetProgress();

    try {
      for (const stepId of PROGRESS_SEQUENCE.slice(0, -2)) {
        await publishProgress(stepId, "active");
        await publishProgress(stepId, "complete");
      }

      await publishProgress("ai", "active");
      const response = await runInvestigation();
      await publishProgress("ai", "complete");
      await publishProgress("root-cause", "complete");

      setDiagnosis(response.diagnosis);
      await saveInvestigationHistory(user.id, response);
      await historyQuery.refetch();
    } catch (caughtError) {
      await publishProgress("root-cause", "error");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Investigation failed",
      );
    } finally {
      setIsInvestigating(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col justify-between gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-600">
              AI Kubernetes Agent
            </p>
            <h1 className="mt-2 text-3xl font-bold text-slate-950">
              Troubleshoot Kubernetes with AI
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Signed in as {user?.email ?? "authenticated user"}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              Realtime: {isRealtimeReady ? "Connected" : "Local fallback"}
            </span>
            <button
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              onClick={signOut}
              type="button"
            >
              Sign out
            </button>
          </div>
        </header>

        <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-xl font-bold text-slate-950">
                Start a cluster investigation
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Collect Kubernetes evidence, run AI reasoning, and save the result.
              </p>
            </div>
            <button
              className="rounded-full bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
              disabled={isInvestigating}
              onClick={handleInvestigate}
              type="button"
            >
              {isInvestigating ? "Investigating..." : "Investigate Cluster"}
            </button>
          </div>
          {error ? (
            <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </p>
          ) : null}
        </section>

        <div className="mt-6 grid gap-6 lg:grid-cols-[360px_1fr]">
          <ProgressList steps={steps} />
          <DiagnosisCard diagnosis={diagnosis} />
        </div>

        <div className="mt-6">
          <HistoryTable
            history={historyQuery.data ?? []}
            isLoading={historyQuery.isLoading}
          />
        </div>
      </div>
    </main>
  );
}
