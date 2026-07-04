import { apiClient } from "@/services/api";
import { HealthResponse } from "@/types/health";

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}
