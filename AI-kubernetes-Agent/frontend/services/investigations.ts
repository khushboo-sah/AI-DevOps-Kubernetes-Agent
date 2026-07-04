import { apiClient } from "@/services/api";
import { insforge } from "@/services/insforge";
import {
  InvestigationHistoryRecord,
  InvestigationProgressRecord,
  InvestigationResponse,
  ProgressStatus,
} from "@/types/investigation";

export async function runInvestigation(): Promise<InvestigationResponse> {
  const response = await apiClient.post<InvestigationResponse>("/investigate");
  return response.data;
}

export async function fetchInvestigationHistory(
  userId: string,
): Promise<InvestigationHistoryRecord[]> {
  const { data, error } = await insforge.database
    .from("investigations")
    .select("id, root_cause, namespace, confidence, status, created_at")
    .eq("user_id", userId)
    .order("created_at", { ascending: false })
    .limit(5);

  if (error) {
    throw new Error(error.message);
  }

  return (data ?? []) as InvestigationHistoryRecord[];
}

export async function saveInvestigationHistory(
  userId: string,
  response: InvestigationResponse,
): Promise<string | null> {
  const namespace = getPrimaryNamespace(response);

  const { data, error } = await insforge.database
    .from("investigations")
    .insert([
      {
        user_id: userId,
        root_cause: response.diagnosis.root_cause,
        namespace,
        confidence: response.diagnosis.confidence,
        status: response.status,
        diagnosis: response.diagnosis,
      },
    ])
    .select("id");

  if (error) {
    throw new Error(error.message);
  }

  const createdRecord = (data?.[0] as { id?: string } | undefined) ?? null;
  return createdRecord?.id ?? null;
}

export async function saveInvestigationProgress(params: {
  userId: string;
  runId: string;
  stepId: string;
  stepLabel: string;
  status: ProgressStatus;
}): Promise<void> {
  const { error } = await insforge.database.from("investigation_progress").insert([
    {
      user_id: params.userId,
      run_id: params.runId,
      step_id: params.stepId,
      step_label: params.stepLabel,
      status: params.status,
    },
  ]);

  if (error) {
    throw new Error(error.message);
  }
}

export async function linkInvestigationProgress(
  userId: string,
  runId: string,
  investigationId: string,
): Promise<void> {
  const { error } = await insforge.database
    .from("investigation_progress")
    .update({ investigation_id: investigationId })
    .eq("user_id", userId)
    .eq("run_id", runId);

  if (error) {
    throw new Error(error.message);
  }
}

export async function fetchInvestigationProgress(
  userId: string,
  runId: string,
): Promise<InvestigationProgressRecord[]> {
  const { data, error } = await insforge.database
    .from("investigation_progress")
    .select("id, investigation_id, run_id, step_id, step_label, status, created_at")
    .eq("user_id", userId)
    .eq("run_id", runId)
    .order("created_at", { ascending: true });

  if (error) {
    throw new Error(error.message);
  }

  return (data ?? []) as InvestigationProgressRecord[];
}

function getPrimaryNamespace(response: InvestigationResponse): string | null {
  const firstPod = response.investigation.pods.problematic_pods[0];
  if (firstPod?.namespace) {
    return firstPod.namespace;
  }

  const firstDeployment =
    response.investigation.deployments.unhealthy_deployments[0];
  if (firstDeployment?.namespace) {
    return firstDeployment.namespace;
  }

  return null;
}
