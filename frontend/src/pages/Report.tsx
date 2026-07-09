import { useLocation, useNavigate } from "react-router-dom";
import type { AnalysisResult, AnalyzeResponse, HistoryItem } from "../types";

function severityClasses(severity: string) {
  if (severity === "high") return "bg-red-500/20 text-red-300";
  if (severity === "low") return "bg-emerald-500/20 text-emerald-300";
  return "bg-amber-500/20 text-amber-300";
}

function copyToClipboard(value: string) {
  navigator.clipboard.writeText(value);
}

export default function Report() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as
    | { result?: AnalyzeResponse; historyItem?: HistoryItem }
    | undefined;

  const result = state?.result;
  const historyItem = state?.historyItem;
  const analysis: AnalysisResult | undefined =
    result?.analysis ?? historyItem?.analysis_result;
  const resourceGroup =
    result?.resource_group ?? historyItem?.resource_group ?? "Unknown";

  if (!analysis) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-16 text-center">
        <p className="text-slate-400">No analysis report available.</p>
        <button
          type="button"
          onClick={() => navigate("/")}
          className="mt-4 rounded-xl bg-sky-500 px-4 py-2 font-medium text-slate-950"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.2em] text-sky-300">
          Analysis Report
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-white">
          {resourceGroup}
        </h1>
        <p className="mt-3 text-slate-300">{analysis.summary}</p>
        <p className="mt-4 text-lg font-medium text-emerald-300">
          Estimated savings: ${analysis.estimated_total_savings_usd}/month
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Issues Found</h2>
        {analysis.issues.length === 0 ? (
          <p className="text-slate-400">No cost issues detected.</p>
        ) : (
          analysis.issues.map((issue) => (
            <article
              key={`${issue.title}-${issue.resource_name}`}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"
            >
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-lg font-medium text-white">{issue.title}</h3>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${severityClasses(issue.severity)}`}
                >
                  {issue.severity}
                </span>
              </div>
              <p className="mt-3 text-slate-300">{issue.description}</p>
              {issue.fix_commands.length > 0 ? (
                <div className="mt-4 space-y-2">
                  {issue.fix_commands.map((command) => (
                    <div
                      key={command}
                      className="flex items-start justify-between gap-3 rounded-xl bg-slate-950 p-4"
                    >
                      <code className="overflow-x-auto text-sm text-sky-200">
                        {command}
                      </code>
                      <button
                        type="button"
                        onClick={() => copyToClipboard(command)}
                        className="shrink-0 rounded-lg border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:border-slate-500"
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              ) : null}
            </article>
          ))
        )}
      </section>

      {analysis.fix_commands.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-white">Recommended Fixes</h2>
          <div className="mt-4 space-y-2">
            {analysis.fix_commands.map((command) => (
              <div
                key={command}
                className="flex items-start justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/70 p-4"
              >
                <code className="overflow-x-auto text-sm text-sky-200">
                  {command}
                </code>
                <button
                  type="button"
                  onClick={() => copyToClipboard(command)}
                  className="shrink-0 rounded-lg border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:border-slate-500"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
