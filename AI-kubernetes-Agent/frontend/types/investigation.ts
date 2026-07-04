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
  status: "success";
  investigation: {
    pods: {
      healthy: boolean;
      problematic_pods: Array<{
        name: string;
        namespace: string;
        status: string;
      }>;
    };
    logs: unknown;
    events: unknown;
    deployments: {
      unhealthy_deployments: Array<{
        name: string;
        namespace: string;
      }>;
    };
    network: unknown;
  };
  diagnosis: Diagnosis;
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
