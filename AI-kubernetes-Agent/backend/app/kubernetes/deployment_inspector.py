"""Inspect Kubernetes deployments using kubectl."""

from typing import Any

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.investigation import (
    DeploymentCondition,
    DeploymentInspectionResult,
    DeploymentIssue,
)


class DeploymentInspector:
    """Inspect deployment replica health and rollout conditions."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()

    def inspect(self) -> DeploymentInspectionResult:
        """Inspect deployments across all namespaces."""

        result, data = self.executor.run_json(["get", "deployments", "-A", "-o", "json"])
        if not result.success or data is None:
            return DeploymentInspectionResult(
                healthy=False,
                errors=[result.error_message],
            )

        items = data.get("items", [])
        unhealthy_deployments = [
            issue
            for deployment in items
            if (issue := self._build_issue_if_unhealthy(deployment)) is not None
        ]

        return DeploymentInspectionResult(
            healthy=len(unhealthy_deployments) == 0,
            checked_count=len(items),
            unhealthy_deployments=unhealthy_deployments,
        )

    def _build_issue_if_unhealthy(
        self,
        deployment: dict[str, Any],
    ) -> DeploymentIssue | None:
        metadata = deployment.get("metadata", {})
        spec = deployment.get("spec", {})
        status = deployment.get("status", {})

        desired_replicas = spec.get("replicas", 1)
        available_replicas = status.get("availableReplicas", 0)
        unavailable_replicas = status.get("unavailableReplicas", 0)
        conditions = [
            DeploymentCondition(
                type=condition.get("type", "Unknown"),
                status=condition.get("status", "Unknown"),
                reason=condition.get("reason"),
                message=condition.get("message"),
            )
            for condition in status.get("conditions", [])
        ]

        has_failed_condition = any(
            condition.type == "Progressing" and condition.status == "False"
            for condition in conditions
        )
        is_unavailable = available_replicas < desired_replicas or unavailable_replicas > 0

        if not is_unavailable and not has_failed_condition:
            return None

        return DeploymentIssue(
            name=metadata.get("name", "unknown"),
            namespace=metadata.get("namespace", "default"),
            desired_replicas=desired_replicas,
            available_replicas=available_replicas,
            unavailable_replicas=unavailable_replicas,
            conditions=conditions,
        )
