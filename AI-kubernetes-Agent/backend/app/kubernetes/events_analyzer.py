"""Analyze Kubernetes events for common failure signals."""

from typing import Any

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.investigation import EventFinding, EventsAnalysisResult

IMPORTANT_REASONS = {
    "FailedScheduling",
    "BackOff",
    "FailedMount",
    "FailedPull",
    "ErrImagePull",
    "Unhealthy",
}


class EventsAnalyzer:
    """Read Kubernetes events and summarize relevant warnings."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()

    def analyze(self) -> EventsAnalysisResult:
        """Analyze all namespace events."""

        result, data = self.executor.run_json(["get", "events", "-A", "-o", "json"])
        if not result.success or data is None:
            return EventsAnalysisResult(
                healthy=False,
                errors=[result.error_message],
            )

        findings = [
            self._build_finding(event)
            for event in data.get("items", [])
            if self._is_relevant(event)
        ]

        return EventsAnalysisResult(
            healthy=len(findings) == 0,
            findings=findings,
        )

    def _is_relevant(self, event: dict[str, Any]) -> bool:
        reason = event.get("reason", "")
        event_type = event.get("type", "")
        message = event.get("message", "").lower()

        return (
            reason in IMPORTANT_REASONS
            or event_type == "Warning"
            or "dns" in message
        )

    def _build_finding(self, event: dict[str, Any]) -> EventFinding:
        metadata = event.get("metadata", {})
        involved_object = event.get("involvedObject", {})

        return EventFinding(
            namespace=metadata.get("namespace", "default"),
            reason=event.get("reason", "Unknown"),
            message=event.get("message", ""),
            involved_object_kind=involved_object.get("kind"),
            involved_object_name=involved_object.get("name"),
            count=event.get("count"),
            last_timestamp=(
                event.get("lastTimestamp")
                or event.get("eventTime")
                or metadata.get("creationTimestamp")
            ),
        )
