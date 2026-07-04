export type ClusterContext = {
  name: string;
  cluster: string;
  user: string;
  namespace: string | null;
  cluster_server: string | null;
  is_current: boolean;
};

export type ClusterListResponse = {
  kubeconfig_path: string | null;
  kubeconfig_found: boolean;
  current_context: string | null;
  contexts: ClusterContext[];
  errors: string[];
};

export type Diagnosis = {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_command: string;
  kubectl_commands: string[];
  prevention_recommendation: string;
  confidence: number;
  confidence_reasoning: string[];
  source: string;
  errors: string[];
};

export type InvestigationResponse = {
  status: "success" | "partial" | "healthy" | "error";
  cluster_context: string | null;
  message?: string | null;
  investigation: {
    cluster_context: string | null;
    pods: {
      healthy: boolean;
      problematic_pods: Array<{
        name: string;
        namespace: string;
        status: string;
      }>;
      errors: string[];
    };
    logs: {
      errors: string[];
    };
    events: {
      findings: Array<{ reason: string; message: string }>;
      errors: string[];
    };
    deployments: {
      unhealthy_deployments: Array<{
        name: string;
        namespace: string;
      }>;
      errors: string[];
    };
    network: {
      issues: Array<{ type: string; message: string }>;
      errors: string[];
    };
  };
  diagnosis: Diagnosis;
  errors: string[];
};

export type InvestigationHistoryRecord = {
  id: string;
  root_cause: string;
  namespace: string | null;
  confidence: number;
  status: string;
  created_at: string;
};

export type ProgressStatus = "pending" | "active" | "complete" | "error";

export type ProgressStep = {
  id: string;
  label: string;
  status: ProgressStatus;
};

export type InvestigationProgressRecord = {
  id: string;
  investigation_id: string | null;
  run_id: string;
  step_id: string;
  step_label: string;
  status: ProgressStatus;
  created_at: string;
};
