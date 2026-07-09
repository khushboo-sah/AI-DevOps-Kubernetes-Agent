interface ProgressTrackerProps {
  messages: string[];
  isRunning: boolean;
}

function stepStatus(index: number, total: number, isRunning: boolean) {
  if (index < total - 1) return "complete";
  if (isRunning) return "active";
  return "complete";
}

export default function ProgressTracker({
  messages,
  isRunning,
}: ProgressTrackerProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Live Progress</h2>
        {isRunning ? (
          <span className="progress-pulse rounded-full bg-sky-500/20 px-3 py-1 text-xs font-medium text-sky-300">
            Running
          </span>
        ) : (
          <span className="rounded-full bg-slate-700/60 px-3 py-1 text-xs font-medium text-slate-300">
            Idle
          </span>
        )}
      </div>

      <div className="space-y-3">
        {messages.length === 0 ? (
          <p className="text-sm text-slate-400">
            Start an analysis to see live progress updates.
          </p>
        ) : (
          messages.map((message, index) => {
            const status = stepStatus(index, messages.length, isRunning);
            const isError = message.startsWith("Error:");

            return (
              <div
                key={`${message}-${index}`}
                className={`progress-step flex items-start gap-3 rounded-xl border px-4 py-3 ${
                  isError
                    ? "border-red-500/40 bg-red-500/10"
                    : "border-slate-800 bg-slate-950/60"
                }`}
                style={{ animationDelay: `${index * 80}ms` }}
              >
                <span
                  className={`mt-1 flex h-5 w-5 items-center justify-center rounded-full text-xs font-bold ${
                    isError
                      ? "bg-red-500/30 text-red-200"
                      : status === "complete"
                        ? "bg-emerald-500/30 text-emerald-200"
                        : "bg-sky-500/30 text-sky-200 progress-pulse"
                  }`}
                >
                  {isError ? "!" : status === "complete" ? "✓" : "•"}
                </span>
                <p
                  className={`text-sm ${
                    isError ? "text-red-200" : "text-slate-200"
                  }`}
                >
                  {message}
                </p>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
