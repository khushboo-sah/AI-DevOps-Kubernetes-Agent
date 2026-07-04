"""Confidence scoring for Kubernetes diagnoses."""

from app.models.investigation import InvestigationPayload


class ConfidenceEngine:
    """Score diagnosis confidence based on evidence quality."""

    def score(self, root_cause: str, investigation: InvestigationPayload) -> tuple[int, list[str]]:
        """Return confidence percentage and short reasoning bullets."""

        score = 40
        reasons: list[str] = []

        if investigation.pods.problematic_pods:
            score += 15
            reasons.append("Problematic pod status was detected.")

        if any(log.findings for log in investigation.logs.logs):
            score += 20
            reasons.append("Logs contain relevant failure messages.")

        if investigation.events.findings:
            score += 15
            reasons.append("Kubernetes events provide failure signals.")

        if investigation.deployments.unhealthy_deployments:
            score += 10
            reasons.append("Deployment health confirms rollout or availability impact.")

        if investigation.network.issues:
            score += 10
            reasons.append("Networking checks found service or endpoint issues.")

        if "No clear Kubernetes failure" in root_cause:
            score = 35
            reasons.append("No strong failure pattern was found in the collected evidence.")

        if "kubectl access" in root_cause:
            score = 25
            reasons.append("Cluster evidence is incomplete because kubectl access failed.")

        if not reasons:
            reasons.append("Diagnosis is based on limited available evidence.")

        return min(score, 95), reasons
