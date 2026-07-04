import { ClusterContext } from "@/types/investigation";

type ClusterSelectorProps = {
  clusters: ClusterContext[];
  selectedContext: string | null;
  onSelect: (contextName: string) => void;
  isLoading: boolean;
  error: string | null;
};

export function ClusterSelector({
  clusters,
  selectedContext,
  onSelect,
  isLoading,
  error,
}: ClusterSelectorProps) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        Loading clusters from your kubeconfig...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 whitespace-pre-line">
        {error}
      </div>
    );
  }

  if (clusters.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
        No Kubernetes clusters were found in your kubeconfig. Mount ~/.kube in Docker
        or set KUBECONFIG_PATH on the backend.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm font-semibold text-slate-700">
        Select a cluster from your kubeconfig
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {clusters.map((cluster) => {
          const isSelected = selectedContext === cluster.name;
          return (
            <button
              className={
                isSelected
                  ? "rounded-2xl border-2 border-blue-600 bg-blue-50 p-4 text-left shadow-sm transition"
                  : "rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-blue-300 hover:bg-slate-50"
              }
              key={cluster.name}
              onClick={() => onSelect(cluster.name)}
              type="button"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-950">{cluster.name}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Cluster: {cluster.cluster}
                  </p>
                  {cluster.cluster_server ? (
                    <p className="mt-1 truncate text-xs text-slate-500">
                      {cluster.cluster_server}
                    </p>
                  ) : null}
                </div>
                {cluster.is_current ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
                    Current
                  </span>
                ) : null}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
