import { Diagnosis } from "@/types/investigation";

type ProblematicPod = {
  name: string;
  namespace: string;
  status: string;
};

type DiagnosisCardProps = {
  diagnosis: Diagnosis | null;
  problematicPods?: ProblematicPod[];
  isInvestigating: boolean;
  isHealthy?: boolean;
  message?: string | null;
  warnings?: string[];
};

function statusBadgeClass(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized.includes("crashloop") || normalized === "error") {
    return "rounded-full bg-red-100 px-2.5 py-1 text-xs font-bold uppercase tracking-wide text-red-700";
  }
  if (normalized.includes("imagepull") || normalized.includes("errimage")) {
    return "rounded-full bg-orange-100 px-2.5 py-1 text-xs font-bold uppercase tracking-wide text-orange-700";
  }
  if (normalized.includes("oom")) {
    return "rounded-full bg-purple-100 px-2.5 py-1 text-xs font-bold uppercase tracking-wide text-purple-700";
  }
  return "rounded-full bg-amber-100 px-2.5 py-1 text-xs font-bold uppercase tracking-wide text-amber-700";
}

export function DiagnosisCard({
  diagnosis,
  problematicPods = [],
  isInvestigating,
  isHealthy = false,
  message,
  warnings = [],
}: DiagnosisCardProps) {
  if (isInvestigating) {
    return (
      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
          Investigating
        </p>
        <h2 className="mt-2 text-2xl font-bold text-slate-950">
          Investigating Kubernetes Cluster...
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Collecting evidence, analyzing events, and running AI reasoning.
        </p>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-blue-100">
          <div className="h-full w-1/2 animate-pulse rounded-full bg-blue-500" />
        </div>
      </div>
    );
  }

  if (!diagnosis) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        Choose a cluster and click Investigate Cluster to generate a diagnosis.
      </div>
    );
  }

  const confidenceClass = isHealthy
    ? "rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700"
    : "rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700";

  return (
    <div
      className={
        isHealthy
          ? "rounded-2xl border border-emerald-200 bg-emerald-50/40 p-6 shadow-sm"
          : "rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      }
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
            {isHealthy ? "Healthy Cluster" : "Diagnosis"}
          </p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">
            {isHealthy ? "No Critical Issues Detected" : "Root Cause"}
          </h2>
          {message ? (
            <p className="mt-2 text-sm text-slate-600">{message}</p>
          ) : null}
        </div>
        <div className={confidenceClass}>{diagnosis.confidence}% confidence</div>
      </div>

      {warnings.length > 0 ? (
        <div className="mt-4 space-y-2">
          {warnings.map((warning) => (
            <p
              className="rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-900"
              key={warning}
            >
              {warning}
            </p>
          ))}
        </div>
      ) : null}

      <dl className="mt-6 space-y-5">
        {problematicPods.length > 0 ? (
          <div>
            <dt className="text-sm font-semibold text-slate-500">
              Kubernetes Pod Status
            </dt>
            <dd className="mt-2 space-y-2">
              {problematicPods.map((pod) => (
                <div
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
                  key={`${pod.namespace}/${pod.name}`}
                >
                  <div>
                    <p className="font-medium text-slate-950">
                      {pod.namespace}/{pod.name}
                    </p>
                  </div>
                  <span className={statusBadgeClass(pod.status)}>{pod.status}</span>
                </div>
              ))}
            </dd>
          </div>
        ) : null}
        <div>
          <dt className="text-sm font-semibold text-slate-500">Root Cause</dt>
          <dd className="mt-1 text-base font-medium text-slate-950">
            {diagnosis.root_cause}
          </dd>
        </div>
        <div>
          <dt className="text-sm font-semibold text-slate-500">Explanation</dt>
          <dd className="mt-1 text-sm leading-6 text-slate-700">
            {diagnosis.explanation}
          </dd>
        </div>
        <div>
          <dt className="text-sm font-semibold text-slate-500">Suggested Fix</dt>
          <dd className="mt-1 text-sm leading-6 text-slate-700">{diagnosis.fix}</dd>
        </div>
        {diagnosis.kubectl_commands.length > 0 ? (
          <div>
            <dt className="text-sm font-semibold text-slate-500">
              kubectl Commands
            </dt>
            <dd className="mt-2 space-y-2">
              {diagnosis.kubectl_commands.map((command) => (
                <pre
                  className="overflow-x-auto rounded-xl bg-slate-950 px-4 py-3 font-mono text-sm text-white"
                  key={command}
                >
                  {command}
                </pre>
              ))}
            </dd>
          </div>
        ) : (
          <div>
            <dt className="text-sm font-semibold text-slate-500">kubectl Command</dt>
            <dd className="mt-2 rounded-xl bg-slate-950 px-4 py-3 font-mono text-sm text-white">
              {diagnosis.kubectl_command || "No command returned"}
            </dd>
          </div>
        )}
        {diagnosis.source ? (
          <div>
            <dt className="text-sm font-semibold text-slate-500">Reasoning Source</dt>
            <dd className="mt-1 text-sm text-slate-700">
              {diagnosis.source === "llm" ? "AI (OpenRouter)" : "Rule-based fallback"}
            </dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}
