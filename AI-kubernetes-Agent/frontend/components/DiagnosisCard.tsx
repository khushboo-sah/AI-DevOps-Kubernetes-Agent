import { Diagnosis } from "@/types/investigation";

type DiagnosisCardProps = {
  diagnosis: Diagnosis | null;
};

export function DiagnosisCard({ diagnosis }: DiagnosisCardProps) {
  if (!diagnosis) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        Diagnosis will appear here after the investigation finishes.
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
            Diagnosis
          </p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Root Cause</h2>
        </div>
        <div className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">
          {diagnosis.confidence}% confidence
        </div>
      </div>

      <dl className="mt-6 space-y-5">
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
        <div>
          <dt className="text-sm font-semibold text-slate-500">kubectl Command</dt>
          <dd className="mt-2 rounded-xl bg-slate-950 px-4 py-3 font-mono text-sm text-white">
            {diagnosis.kubectl_command || "No command returned"}
          </dd>
        </div>
      </dl>
    </div>
  );
}
