"""Rule-assisted root cause analysis for Kubernetes evidence."""

from app.models.investigation import InvestigationPayload


class RootCauseAnalyzer:
    """Infer a likely root cause from investigation evidence."""

    def analyze(self, investigation: InvestigationPayload) -> str:
        """Return a concise root cause guess from strong signals."""

        log_text = self._combined_log_text(investigation)
        pod_statuses = {pod.status for pod in investigation.pods.problematic_pods}
        event_reasons = {event.reason for event in investigation.events.findings}

        if self._mentions_missing_env(log_text):
            return "Application startup is failing because a required environment variable is missing."

        if "ImagePullBackOff" in pod_statuses or "ErrImagePull" in event_reasons:
            return "A workload cannot start because Kubernetes cannot pull the container image."

        if "CrashLoopBackOff" in pod_statuses:
            return "A container is repeatedly crashing during startup."

        if "OOMKilled" in pod_statuses:
            return "A container is being killed because it is exceeding its memory limit."

        if "FailedScheduling" in event_reasons or "Pending" in pod_statuses:
            return "Pods are not being scheduled, likely because cluster resources or scheduling constraints are blocking placement."

        if any(issue.type == "selector_mismatch" for issue in investigation.network.issues):
            return "A service selector does not match the intended pods, so traffic cannot reach the workload."

        if any(issue.type in {"missing_endpoints", "no_ready_endpoints"} for issue in investigation.network.issues):
            return "A service has no ready endpoints, so requests cannot be routed to healthy pods."

        if investigation.deployments.unhealthy_deployments:
            return "One or more deployments are unavailable or stuck during rollout."

        if self._has_kubectl_errors(investigation):
            return "Kubernetes evidence could not be fully collected because kubectl access is unavailable or failing."

        return "No clear Kubernetes failure was detected from the collected evidence."

    def _combined_log_text(self, investigation: InvestigationPayload) -> str:
        findings = []
        for log_summary in investigation.logs.logs:
            findings.extend(log_summary.findings)
            if log_summary.error:
                findings.append(log_summary.error)
        return "\n".join(findings).lower()

    def _mentions_missing_env(self, text: str) -> bool:
        return (
            "environment variable" in text
            or "missing env" in text
            or "database_url" in text and "missing" in text
        )

    def _has_kubectl_errors(self, investigation: InvestigationPayload) -> bool:
        return any(
            section_errors
            for section_errors in (
                investigation.pods.errors,
                investigation.logs.errors,
                investigation.events.errors,
                investigation.deployments.errors,
                investigation.network.errors,
            )
        )
