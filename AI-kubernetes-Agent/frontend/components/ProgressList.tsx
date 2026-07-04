import { ProgressStep } from "@/types/investigation";

type ProgressListProps = {
  steps: ProgressStep[];
};

export function ProgressList({ steps }: ProgressListProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">Investigation Status</h2>
      <div className="mt-4 space-y-3">
        {steps.map((step) => (
          <div className="flex items-center gap-3" key={step.id}>
            <span
              className={
                step.status === "complete"
                  ? "flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-700"
                  : step.status === "active"
                    ? "flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700"
                    : step.status === "error"
                      ? "flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-sm font-bold text-red-700"
                      : "flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-400"
              }
            >
              {step.status === "complete" ? "✓" : step.status === "error" ? "!" : "•"}
            </span>
            <span className="text-sm font-medium text-slate-700">{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
