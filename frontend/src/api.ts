import { clearAuth, getToken } from "./auth";
import type {
  AnalyzeResponse,
  AuthResponse,
  HistoryItem,
  ResourceGroup,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAuth();
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message =
      typeof errorBody.detail === "string"
        ? errorBody.detail
        : "Request failed";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function signup(email: string, password: string) {
  return request<AuthResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string) {
  return request<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function fetchResourceGroups() {
  return request<{ resource_groups: ResourceGroup[]; count: number }>(
    "/api/resource-groups",
  );
}

export function runAnalysis(resourceGroup: string, analysisId: string) {
  return request<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({
      resource_group: resourceGroup,
      analysis_id: analysisId,
    }),
  });
}

export function fetchHistory() {
  return request<{ analyses: HistoryItem[]; count: number }>("/api/history");
}

export function createProgressSocket(analysisId: string) {
  const apiBase = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
  const wsBase = apiBase.replace(/^http/, "ws");
  return new WebSocket(`${wsBase}/ws/progress/${analysisId}`);
}
