import { InvestigationHistoryRecord } from "@/types/investigation";

type HistoryTableProps = {
  history: InvestigationHistoryRecord[];
  isLoading: boolean;
};

export function HistoryTable({ history, isLoading }: HistoryTableProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">Recent Investigations</h2>
      <div className="mt-4 overflow-hidden rounded-xl border border-slate-100">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3 font-semibold">Root Cause</th>
              <th className="px-4 py-3 font-semibold">Namespace</th>
              <th className="px-4 py-3 font-semibold">Confidence</th>
              <th className="px-4 py-3 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr>
                <td className="px-4 py-4 text-slate-500" colSpan={4}>
                  Loading history...
                </td>
              </tr>
            ) : history.length === 0 ? (
              <tr>
                <td className="px-4 py-4 text-slate-500" colSpan={4}>
                  No previous investigations yet.
                </td>
              </tr>
            ) : (
              history.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {item.root_cause}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {item.namespace ?? "default"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {item.confidence}%
                  </td>
                  <td className="px-4 py-3 text-slate-600">{item.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
