import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchHistory } from "../api";
import type { HistoryItem } from "../types";

export default function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory()
      .then((response) => setItems(response.analyses))
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load history");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-white">Analysis History</h1>
        <p className="mt-2 text-slate-400">
          Review previous investigations and open full reports.
        </p>
      </div>

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      <div className="space-y-4">
        {loading ? (
          <p className="text-slate-400">Loading analysis history...</p>
        ) : items.length === 0 ? (
          <p className="text-slate-400">No analyses stored yet.</p>
        ) : (
          items.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() =>
                navigate("/report", { state: { historyItem: item } })
              }
              className="flex w-full items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-5 py-4 text-left hover:border-sky-500/40"
            >
              <div>
                <p className="font-medium text-white">{item.resource_group}</p>
                <p className="mt-1 text-sm text-slate-400">
                  {new Date(item.created_at).toLocaleString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-300">
                  {item.issues_found} issues
                </p>
                <p className="mt-1 text-sm font-medium text-emerald-300">
                  {item.estimated_savings}
                </p>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
