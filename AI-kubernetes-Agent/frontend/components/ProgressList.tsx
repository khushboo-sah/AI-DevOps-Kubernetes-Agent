import { ProgressStep } from "@/types/investigation";

type ProgressListProps = {
  steps: ProgressStep[];
  isInvestigating: boolean;
  hasIssues?: boolean;
  isHealthy?: boolean;
};

export function ProgressList({
  steps,
  isInvestigating,
  hasIssues = false,
  isHealthy = false,
}: ProgressListProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">
        {isInvestigating ? "Investigation Status" : "Investigation Steps"}
      </h2>

      {isInvestigating ? (
        <p className="mt-1 text-sm text-slate-600">
          Investigating Kubernetes Cluster...
        </p>
      ) : hasIssues ? (
        <p className="mt-2 rounded-xl bg-red-50 px-3 py-2 text-sm font-medium text-red-800">
          Issues found in the cluster — see diagnosis.
        </p>
      ) : isHealthy ? (
        <p className="mt-2 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800">
          No critical issues detected.
        </p>
      ) : (
        <p className="mt-1 text-sm text-slate-500">
          Green checks mean each step finished — not that the cluster is healthy.
        </p>
      )}

      <div className="mt-4 space-y-3">
        {steps.map((step) => {
          const isIssueStep = hasIssues && step.id === "root-cause" && step.status === "complete";

          return (
            <div className="flex items-center gap-3" key={step.id}>
              <span
                className={
                  isIssueStep
                    ? "flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-sm font-bold text-red-700"
                    : step.status === "complete"
                      ? "flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-700"
                      : step.status === "active"
                        ? "flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 animate-pulse"
                        : step.status === "error"
                          ? "flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-sm font-bold text-red-700"
                          : "flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-400"
                }
              >
                {isIssueStep ? "!" : step.status === "complete" ? "✓" : step.status === "error" ? "!" : "•"}
              </span>
              <span
                className={
                  isIssueStep
                    ? "text-sm font-semibold text-red-700"
                    : step.status === "active"
                      ? "text-sm font-semibold text-blue-700"
                      : "text-sm font-medium text-slate-700"
                }
              >
                {isIssueStep
                  ? "Issue identified"
                  : step.status === "complete"
                    ? `✓ ${step.label}`
                    : step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
