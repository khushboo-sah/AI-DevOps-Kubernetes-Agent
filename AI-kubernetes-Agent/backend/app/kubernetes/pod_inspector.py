"""Pod inspection using kubectl."""

from typing import Any

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.investigation import PodInspectionResult, PodIssue

UNHEALTHY_REASONS = {
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "Pending",
    "Error",
    "Failed",
    "OOMKilled",
    "ContainerCreating",
}


class PodInspector:
    """Collect pod status and flag unhealthy pods."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()

    def inspect(self) -> PodInspectionResult:
        """Inspect all pods in all namespaces."""

        result, data = self.executor.run_json(["get", "pods", "-A", "-o", "json"])
        if not result.success or data is None:
            return PodInspectionResult(
                healthy=False,
                errors=[result.error_message],
            )

        items = data.get("items", [])
        problematic_pods = [
            issue
            for pod in items
            if (issue := self._build_issue_if_unhealthy(pod)) is not None
        ]

        return PodInspectionResult(
            healthy=len(problematic_pods) == 0,
            checked_count=len(items),
            problematic_pods=problematic_pods,
        )

    def _build_issue_if_unhealthy(self, pod: dict[str, Any]) -> PodIssue | None:
        metadata = pod.get("metadata", {})
        status = pod.get("status", {})
        namespace = metadata.get("namespace", "default")
        name = metadata.get("name", "unknown")
        phase = status.get("phase")
        reason, containers = self._find_container_problem(status)

        if reason is None and phase in UNHEALTHY_REASONS:
            reason = phase

        if reason is None:
            return None

        return PodIssue(
            name=name,
            namespace=namespace,
            status=reason,
            reason=phase,
            containers=containers,
        )

    def _find_container_problem(
        self,
        pod_status: dict[str, Any],
    ) -> tuple[str | None, list[str]]:
        statuses = (
            pod_status.get("initContainerStatuses", [])
            + pod_status.get("containerStatuses", [])
        )

        for container_status in statuses:
            container_name = container_status.get("name", "unknown")
            state = container_status.get("state", {})
            last_state = container_status.get("lastState", {})

            waiting_reason = state.get("waiting", {}).get("reason")
            if waiting_reason in UNHEALTHY_REASONS:
                return waiting_reason, [container_name]

            terminated_reason = state.get("terminated", {}).get("reason")
            if terminated_reason in UNHEALTHY_REASONS:
                return terminated_reason, [container_name]

            last_terminated_reason = last_state.get("terminated", {}).get("reason")
            if last_terminated_reason in UNHEALTHY_REASONS:
                return last_terminated_reason, [container_name]

        return None, []
