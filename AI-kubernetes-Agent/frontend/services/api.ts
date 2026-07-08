import axios, { isAxiosError } from "axios";

import { getAccessToken } from "@/services/authToken";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  timeout: 120000,
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (!isAxiosError(error)) {
      return Promise.reject(
        error instanceof Error ? error : new Error("Request failed"),
      );
    }

    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return Promise.reject(new Error(detail));
    }

    if (error.response?.status === 401) {
      return Promise.reject(
        new Error("Your session expired. Please sign in again."),
      );
    }

    if (error.response?.status === 503) {
      return Promise.reject(
        new Error(
          typeof detail === "string"
            ? detail
            : "The backend could not reach Kubernetes or authentication services.",
        ),
      );
    }

    if (error.code === "ECONNABORTED") {
      return Promise.reject(
        new Error(
          "Investigation timed out. The cluster may be slow or unreachable.",
        ),
      );
    }

    if (!error.response) {
      return Promise.reject(
        new Error(
          "Cannot reach the backend API. Make sure the backend is running on port 8000.",
        ),
      );
    }

    return Promise.reject(
      new Error(error.message || "Investigation request failed"),
    );
  },
);
