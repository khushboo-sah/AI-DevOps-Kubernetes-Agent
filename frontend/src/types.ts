export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
}

export interface ResourceGroup {
  name: string;
  location: string;
  tags: Record<string, string>;
}

export interface AnalysisIssue {
  title: string;
  description: string;
  severity: "high" | "medium" | "low";
  resource_name?: string;
  resource_type?: string;
  estimated_monthly_savings_usd?: number;
  fix_commands: string[];
}

export interface AnalysisResult {
  summary: string;
  issues: AnalysisIssue[];
  estimated_total_savings_usd: number;
  fix_commands: string[];
}

export interface AnalyzeResponse {
  id: number;
  resource_group: string;
  resources: unknown[];
  count: number;
  analysis: AnalysisResult;
}

export interface HistoryItem {
  id: number;
  user_id: number;
  resource_group: string;
  resources_scanned: number;
  issues_found: number;
  estimated_savings: string;
  analysis_result: AnalysisResult;
  status: string;
  created_at: string;
}
