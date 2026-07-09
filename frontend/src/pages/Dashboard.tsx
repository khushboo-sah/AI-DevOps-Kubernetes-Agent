import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createProgressSocket,
  fetchResourceGroups,
  runAnalysis,
} from "../api";
import ProgressTracker from "../components/ProgressTracker";
import type { AnalyzeResponse, ResourceGroup } from "../types";

function waitForSocketOpen(socket: WebSocket): Promise<void> {
  return new Promise((resolve, reject) => {
    if (socket.readyState === WebSocket.OPEN) {
      resolve();
      return;
    }

    socket.onopen = () => resolve();
    socket.onerror = () => reject(new Error("WebSocket connection failed."));
  });
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [resourceGroups, setResourceGroups] = useState<ResourceGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState("");
  const [loadingGroups, setLoadingGroups] = useState(true);

  useEffect(() => {
    fetchResourceGroups()
      .then((response) => {
        setResourceGroups(response.resource_groups);
        if (response.resource_groups.length > 0) {
          setSelectedGroup(response.resource_groups[0].name ?? "");
        }
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load groups");
      })
      .finally(() => setLoadingGroups(false));
  }, []);

  async function handleRunAnalysis() {
    if (!selectedGroup) {
      setError("Select a resource group first.");
      return;
    }

    setError("");
    setProgressMessages([]);
    setIsRunning(true);

    const analysisId = crypto.randomUUID();
    const socket = createProgressSocket(analysisId);

    socket.onmessage = (event) => {
      setProgressMessages((current) => [...current, event.data]);
    };

    try {
      await waitForSocketOpen(socket);
      const result: AnalyzeResponse = await runAnalysis(
        selectedGroup,
        analysisId,
      );
      navigate("/report", { state: { result } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      socket.close();
      setIsRunning(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-white">Dashboard</h1>
        <p className="mt-2 text-slate-400">
          Select a resource group and run an AI-powered cost investigation.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
          <label className="mb-2 block text-sm text-slate-300">
            Azure Resource Group
          </label>
          <select
            value={selectedGroup}
            onChange={(event) => setSelectedGroup(event.target.value)}
            disabled={loadingGroups || isRunning}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none ring-sky-400 focus:ring-2 disabled:opacity-60"
          >
            {resourceGroups.length === 0 ? (
              <option value="">
                {loadingGroups ? "Loading resource groups..." : "No groups found"}
              </option>
            ) : (
              resourceGroups.map((group) => (
                <option key={group.name} value={group.name}>
                  {group.name} ({group.location})
                </option>
              ))
            )}
          </select>

          <button
            type="button"
            onClick={handleRunAnalysis}
            disabled={isRunning || !selectedGroup || loadingGroups}
            className="mt-6 rounded-xl bg-sky-500 px-5 py-3 font-medium text-slate-950 hover:bg-sky-400 disabled:opacity-60"
          >
            {isRunning ? "Running Analysis..." : "Run Analysis"}
          </button>

          {error ? <p className="mt-4 text-sm text-red-400">{error}</p> : null}
        </section>

        <ProgressTracker messages={progressMessages} isRunning={isRunning} />
      </div>
    </div>
  );
}
