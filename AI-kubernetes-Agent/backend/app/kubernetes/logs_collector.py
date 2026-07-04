"""Collect concise logs from problematic pods."""

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.investigation import LogsCollectionResult, PodIssue, PodLogSummary

ERROR_KEYWORDS = (
    "exception",
    "traceback",
    "error",
    "failed",
    "failure",
    "fatal",
    "panic",
    "connection refused",
    "connection reset",
    "timeout",
    "timed out",
    "missing",
    "not found",
    "environment variable",
    "startup",
    "crash",
    "back-off",
    "backoff",
)


class LogsCollector:
    """Fetch and summarize logs for failed pods."""

    def __init__(
        self,
        executor: KubectlExecutor | None = None,
        tail_lines: int = 100,
        max_findings_per_pod: int = 25,
    ) -> None:
        self.executor = executor or KubectlExecutor()
        self.tail_lines = tail_lines
        self.max_findings_per_pod = max_findings_per_pod

    def collect(self, pods: list[PodIssue]) -> LogsCollectionResult:
        """Collect logs for the pods already marked problematic."""

        summaries: list[PodLogSummary] = []
        errors: list[str] = []

        for pod in pods:
            result = self.executor.run(
                [
                    "logs",
                    pod.name,
                    "-n",
                    pod.namespace,
                    "--all-containers=true",
                    f"--tail={self.tail_lines}",
                ],
                timeout_seconds=20,
            )

            if not result.success:
                error = f"{pod.namespace}/{pod.name}: {result.error_message}"
                errors.append(error)
                summaries.append(
                    PodLogSummary(
                        name=pod.name,
                        namespace=pod.namespace,
                        error=result.error_message,
                    )
                )
                continue

            summaries.append(
                PodLogSummary(
                    name=pod.name,
                    namespace=pod.namespace,
                    findings=self._extract_relevant_lines(result.stdout),
                )
            )

        return LogsCollectionResult(
            collected_count=len([summary for summary in summaries if summary.error is None]),
            logs=summaries,
            errors=errors,
        )

    def _extract_relevant_lines(self, output: str) -> list[str]:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        relevant = [
            line
            for line in lines
            if any(keyword in line.lower() for keyword in ERROR_KEYWORDS)
        ]

        if relevant:
            return relevant[-self.max_findings_per_pod :]

        return lines[-10:]
