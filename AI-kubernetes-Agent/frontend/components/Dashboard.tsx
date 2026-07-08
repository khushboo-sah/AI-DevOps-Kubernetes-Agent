"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { ClusterSelector } from "@/components/ClusterSelector";
import { DiagnosisCard } from "@/components/DiagnosisCard";
import { HistoryTable } from "@/components/HistoryTable";
import { ProgressList } from "@/components/ProgressList";
import { useAuthSession } from "@/hooks/useAuthSession";
import { useInvestigationProgress } from "@/hooks/useInvestigationProgress";
import { useHealth } from "@/hooks/useHealth";
import {
  fetchClusters,
  fetchInvestigationHistory,
  linkInvestigationProgress,
  runInvestigation,
  saveInvestigationHistory,
} from "@/services/investigations";
import { Diagnosis, InvestigationResponse } from "@/types/investigation";

const PROGRESS_SEQUENCE = [
  "pods",
  "logs",
  "events",
  "deployments",
  "network",
  "ai",
  "root-cause",
] as const;

const STEP_DELAYS_MS = [400, 400, 400, 400, 400];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function Dashboard() {
  const { accessToken, signOut, user } = useAuthSession();
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [problematicPods, setProblematicPods] = useState<
    InvestigationResponse["investigation"]["pods"]["problematic_pods"]
  >([]);
  const [investigationMessage, setInvestigationMessage] = useState<string | null>(
    null,
  );
  const [investigationStatus, setInvestigationStatus] = useState<
    InvestigationResponse["status"] | null
  >(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [selectedContext, setSelectedContext] = useState<string | null>(null);
  const { isRealtimeReady, publishProgress, resetProgress, steps } =
    useInvestigationProgress(user?.id);

  const healthQuery = useHealth();
  const clustersQuery = useQuery({
    queryKey: ["clusters"],
    queryFn: fetchClusters,
    enabled: Boolean(user?.id && accessToken),
  });

  const historyQuery = useQuery({
    queryKey: ["investigation-history", user?.id],
    queryFn: () => fetchInvestigationHistory(user?.id ?? ""),
    enabled: Boolean(user?.id),
  });

  useEffect(() => {
    if (!clustersQuery.data?.contexts.length) {
      return;
    }

    const current =
      clustersQuery.data.contexts.find((item) => item.is_current) ??
      clustersQuery.data.contexts[0];

    setSelectedContext((previous) => previous ?? current.name);
  }, [clustersQuery.data]);

  async function animateInvestigationSteps(runId: string) {
    for (let index = 0; index < PROGRESS_SEQUENCE.length - 2; index += 1) {
      const stepId = PROGRESS_SEQUENCE[index];
      await publishProgress(stepId, "active", runId);
      await sleep(STEP_DELAYS_MS[index] ?? 400);
      await publishProgress(stepId, "complete", runId);
    }

    await publishProgress("ai", "active", runId);
  }

  async function handleInvestigate() {
    if (!user || !accessToken) {
      setError("Please login before starting an investigation.");
      return;
    }

    if (!selectedContext) {
      setError("Select a Kubernetes cluster from your kubeconfig first.");
      return;
    }

    if (healthQuery.data?.status !== "healthy") {
      setError(
        "Backend API is not reachable. Start the backend service and try again.",
      );
      return;
    }

    setDiagnosis(null);
    setProblematicPods([]);
    setInvestigationMessage(null);
    setInvestigationStatus(null);
    setWarnings([]);
    setError(null);
    setIsInvestigating(true);
    resetProgress();
    const runId = crypto.randomUUID();

    const animationPromise = animateInvestigationSteps(runId);

    try {
      const response = await runInvestigation(selectedContext);
      await animationPromise;

      await publishProgress("ai", "complete", runId);
      await publishProgress("root-cause", "complete", runId);

      setDiagnosis(response.diagnosis);
      setProblematicPods(response.investigation.pods.problematic_pods);
      setInvestigationStatus(response.status);
      setInvestigationMessage(response.message ?? null);

      const nextWarnings = [...response.errors, ...response.diagnosis.errors];
      setWarnings(nextWarnings.filter(Boolean));

      const investigationId = await saveInvestigationHistory(user.id, response);
      if (investigationId) {
        await linkInvestigationProgress(user.id, runId, investigationId);
      }
      await historyQuery.refetch();
    } catch (caughtError) {
      await animationPromise.catch(() => undefined);
      await publishProgress("ai", "error", runId);
      await publishProgress("root-cause", "error", runId);
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Investigation failed",
      );
    } finally {
      setIsInvestigating(false);
    }
  }

  const clusterError =
    clustersQuery.error instanceof Error
      ? clustersQuery.error.message
      : clustersQuery.data?.errors[0] ?? null;

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
            <span
              className={
                healthQuery.data?.status === "healthy"
                  ? "rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
                  : "rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700"
              }
            >
              Backend: {healthQuery.isLoading ? "Checking..." : healthQuery.data?.status ?? "offline"}
            </span>
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
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
            <div className="max-w-2xl">
              <h2 className="text-xl font-bold text-slate-950">
                Start a cluster investigation
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Select a cluster from your kubeconfig, then collect evidence and
                run AI reasoning against real Kubernetes failures.
              </p>
            </div>
            <button
              className="rounded-full bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
              disabled={
                isInvestigating || !selectedContext || healthQuery.data?.status !== "healthy"
              }
              onClick={handleInvestigate}
              type="button"
            >
              {isInvestigating ? "Investigating..." : "Investigate Cluster"}
            </button>
          </div>

          <div className="mt-6">
            <ClusterSelector
              clusters={clustersQuery.data?.contexts ?? []}
              error={clusterError}
              isLoading={clustersQuery.isLoading}
              onSelect={setSelectedContext}
              selectedContext={selectedContext}
            />
          </div>

          {error ? (
            <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 whitespace-pre-line">
              {error}
            </p>
          ) : null}
        </section>

        <div className="mt-6 grid gap-6 lg:grid-cols-[360px_1fr]">
          <ProgressList
            hasIssues={problematicPods.length > 0}
            isHealthy={investigationStatus === "healthy"}
            isInvestigating={isInvestigating}
            steps={steps}
          />
          <DiagnosisCard
            diagnosis={diagnosis}
            isHealthy={investigationStatus === "healthy"}
            isInvestigating={isInvestigating}
            message={investigationMessage}
            problematicPods={problematicPods}
            warnings={warnings}
          />
        </div>

        <div className="mt-6">
          <HistoryTable
            error={
              historyQuery.error instanceof Error
                ? historyQuery.error.message
                : null
            }
            history={historyQuery.data ?? []}
            isLoading={historyQuery.isLoading}
          />
        </div>
      </div>
    </main>
  );
}
