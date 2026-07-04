import { apiClient } from "@/services/api";
import { insforge } from "@/services/insforge";
import {
  InvestigationHistoryRecord,
  InvestigationResponse,
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
): Promise<void> {
  const namespace = getPrimaryNamespace(response);

  const { error } = await insforge.database.from("investigations").insert([
    {
      user_id: userId,
      root_cause: response.diagnosis.root_cause,
      namespace,
      confidence: response.diagnosis.confidence,
      status: response.status,
      diagnosis: response.diagnosis,
    },
  ]);

  if (error) {
    throw new Error(error.message);
  }
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
