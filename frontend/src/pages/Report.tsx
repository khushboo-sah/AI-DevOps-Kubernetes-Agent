import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  inferIssueType,
  issueTypeClasses,
  issueTypeLabel,
} from "../utils/issueType";
import type { AnalysisResult, AnalyzeResponse, HistoryItem } from "../types";

function severityClasses(severity: string) {
  if (severity === "high") return "bg-red-500/20 text-red-300 border-red-500/30";
  if (severity === "low") return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  return "bg-amber-500/20 text-amber-300 border-amber-500/30";
}

async function copyToClipboard(value: string) {
  await navigator.clipboard.writeText(value);
}

export default function Report() {
  const navigate = useNavigate();
  const location = useLocation();
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);
  const state = location.state as
    | { result?: AnalyzeResponse; historyItem?: HistoryItem }
    | undefined;

  const result = state?.result;
  const historyItem = state?.historyItem;
  const analysis: AnalysisResult | undefined =
    result?.analysis ?? historyItem?.analysis_result;
  const resourceGroup =
    result?.resource_group ?? historyItem?.resource_group ?? "Unknown";
  const resourcesScanned =
    result?.count ?? historyItem?.resources_scanned ?? 0;
  const issuesFound =
    historyItem?.issues_found ?? analysis?.issues.length ?? 0;
  const estimatedSavings =
    historyItem?.estimated_savings ??
    `$${analysis?.estimated_total_savings_usd ?? 0}/month`;

  async function handleCopy(command: string) {
    await copyToClipboard(command);
    setCopiedCommand(command);
    window.setTimeout(() => setCopiedCommand(null), 2000);
  }

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
      </div>

      <section className="mb-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-sm text-slate-400">Resources Scanned</p>
          <p className="mt-2 text-3xl font-semibold text-white">
            {resourcesScanned}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-sm text-slate-400">Issues Found</p>
          <p className="mt-2 text-3xl font-semibold text-amber-300">
            {issuesFound}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-sm text-slate-400">Estimated Savings</p>
          <p className="mt-2 text-3xl font-semibold text-emerald-300">
            {estimatedSavings}
          </p>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Issues Found</h2>
        {analysis.issues.length === 0 ? (
          <p className="text-slate-400">No cost issues detected.</p>
        ) : (
          analysis.issues.map((issue) => {
            const issueType = inferIssueType(issue);
            const primaryCommand = issue.fix_commands[0];

            return (
              <article
                key={`${issue.title}-${issue.resource_name}`}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="text-lg font-medium text-white">
                    {issue.resource_name ?? issue.title}
                  </h3>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${issueTypeClasses(issueType)}`}
                  >
                    {issueTypeLabel(issueType)}
                  </span>
                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase ${severityClasses(issue.severity)}`}
                  >
                    {issue.severity}
                  </span>
                </div>

                <p className="mt-2 text-sm text-slate-400">{issue.title}</p>
                <p className="mt-3 text-slate-300">{issue.description}</p>

                {primaryCommand ? (
                  <div className="mt-4 flex items-start justify-between gap-3 rounded-xl bg-slate-950 p-4">
                    <code className="overflow-x-auto text-sm text-sky-200">
                      {primaryCommand}
                    </code>
                    <button
                      type="button"
                      onClick={() => handleCopy(primaryCommand)}
                      className="shrink-0 rounded-lg border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:border-slate-500"
                    >
                      {copiedCommand === primaryCommand ? "Copied" : "Copy"}
                    </button>
                  </div>
                ) : null}
              </article>
            );
          })
        )}
      </section>

      {analysis.fix_commands.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-white">All Fix Commands</h2>
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
                  onClick={() => handleCopy(command)}
                  className="shrink-0 rounded-lg border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:border-slate-500"
                >
                  {copiedCommand === command ? "Copied" : "Copy"}
                </button>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
