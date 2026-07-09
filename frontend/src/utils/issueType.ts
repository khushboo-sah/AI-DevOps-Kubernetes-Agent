import type { AnalysisIssue } from "../types";

export type IssueType = "over-provisioned" | "unused" | "misconfigured" | "optimization";

export function inferIssueType(issue: AnalysisIssue): IssueType {
  const text = `${issue.title} ${issue.description}`.toLowerCase();

  if (
    text.includes("over-provision") ||
    text.includes("oversized") ||
    text.includes("larger than") ||
    text.includes("sizing")
  ) {
    return "over-provisioned";
  }

  if (
    text.includes("unused") ||
    text.includes("idle") ||
    text.includes("orphan") ||
    text.includes("unattached") ||
    text.includes("public ip")
  ) {
    return "unused";
  }

  if (
    text.includes("misconfig") ||
    text.includes("pricing tier") ||
    text.includes("wrong tier") ||
    text.includes("premium") ||
    text.includes("non-prod")
  ) {
    return "misconfigured";
  }

  return "optimization";
}

export function issueTypeLabel(type: IssueType): string {
  switch (type) {
    case "over-provisioned":
      return "Over-provisioned";
    case "unused":
      return "Unused / Idle";
    case "misconfigured":
      return "Misconfigured";
    default:
      return "Cost Optimization";
  }
}

export function issueTypeClasses(type: IssueType): string {
  switch (type) {
    case "over-provisioned":
      return "bg-orange-500/20 text-orange-200";
    case "unused":
      return "bg-violet-500/20 text-violet-200";
    case "misconfigured":
      return "bg-cyan-500/20 text-cyan-200";
    default:
      return "bg-slate-500/20 text-slate-200";
  }
}
