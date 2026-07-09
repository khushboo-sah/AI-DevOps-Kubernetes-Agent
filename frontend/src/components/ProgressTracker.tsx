interface ProgressTrackerProps {
  messages: string[];
  isRunning: boolean;
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
          <span className="rounded-full bg-sky-500/20 px-3 py-1 text-xs font-medium text-sky-300">
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
          messages.map((message, index) => (
            <div
              key={`${message}-${index}`}
              className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3"
            >
              <span className="mt-1 h-2 w-2 rounded-full bg-sky-400" />
              <p className="text-sm text-slate-200">{message}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
