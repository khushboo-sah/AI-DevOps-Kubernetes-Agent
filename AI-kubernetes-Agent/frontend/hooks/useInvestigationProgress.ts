"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { insforge } from "@/services/insforge";
import { ProgressStep, ProgressStatus } from "@/types/investigation";

const INITIAL_STEPS: ProgressStep[] = [
  { id: "pods", label: "Checking Pods", status: "pending" },
  { id: "logs", label: "Reading Logs", status: "pending" },
  { id: "events", label: "Analyzing Events", status: "pending" },
  { id: "deployments", label: "Inspecting Deployments", status: "pending" },
  { id: "network", label: "Checking Networking", status: "pending" },
  { id: "ai", label: "AI Reasoning", status: "pending" },
  { id: "root-cause", label: "Root Cause Found", status: "pending" },
];

type ProgressMessage = {
  stepId: string;
  status: ProgressStatus;
};

export function useInvestigationProgress(userId?: string) {
  const [steps, setSteps] = useState<ProgressStep[]>(INITIAL_STEPS);
  const [isRealtimeReady, setIsRealtimeReady] = useState(false);

  const channel = useMemo(() => {
    return userId ? `investigation:${userId}` : null;
  }, [userId]);

  const applyProgress = useCallback((message: ProgressMessage) => {
    setSteps((currentSteps) =>
      currentSteps.map((step) => {
        if (step.id === message.stepId) {
          return { ...step, status: message.status };
        }

        return step;
      }),
    );
  }, []);

  useEffect(() => {
    if (!channel) {
      return;
    }

    let isMounted = true;

    async function subscribe() {
      try {
        await insforge.realtime.connect();
        const response = await insforge.realtime.subscribe(channel);
        if (isMounted) {
          setIsRealtimeReady(response.ok);
        }
      } catch {
        if (isMounted) {
          setIsRealtimeReady(false);
        }
      }
    }

    insforge.realtime.on<ProgressMessage>("progress_updated", applyProgress);
    subscribe();

    return () => {
      isMounted = false;
      insforge.realtime.off("progress_updated", applyProgress);
      insforge.realtime.unsubscribe(channel);
    };
  }, [applyProgress, channel]);

  const resetProgress = useCallback(() => {
    setSteps(INITIAL_STEPS);
  }, []);

  const publishProgress = useCallback(
    async (stepId: string, status: ProgressStatus) => {
      const message = { stepId, status };
      applyProgress(message);

      if (!channel || !isRealtimeReady) {
        return;
      }

      try {
        await insforge.realtime.publish(channel, "progress_updated", message);
      } catch {
        // Local progress already updated; realtime is best-effort for this MVP.
      }
    },
    [applyProgress, channel, isRealtimeReady],
  );

  return {
    steps,
    isRealtimeReady,
    resetProgress,
    publishProgress,
  };
}
