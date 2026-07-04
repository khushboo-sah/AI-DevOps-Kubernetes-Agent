"""Orchestrate Kubernetes evidence collection."""

from loguru import logger

from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.kubectl_executor import KubectlExecutor
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.pod_inspector import PodInspector
from app.models.investigation import InvestigationPayload


class InvestigationService:
    """Run the Kubernetes investigation workflow."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()
        self.pod_inspector = PodInspector(self.executor)
        self.logs_collector = LogsCollector(self.executor)
        self.events_analyzer = EventsAnalyzer(self.executor)
        self.deployment_inspector = DeploymentInspector(self.executor)
        self.network_inspector = NetworkInspector(self.executor)

    def run_investigation(self) -> InvestigationPayload:
        """Collect Kubernetes troubleshooting evidence in a predictable order."""

        logger.info("Starting Kubernetes investigation")
        pods = self.pod_inspector.inspect()
        logs = self.logs_collector.collect(pods.problematic_pods)
        events = self.events_analyzer.analyze()
        deployments = self.deployment_inspector.inspect()
        network = self.network_inspector.inspect()
        logger.info("Finished Kubernetes investigation")

        return InvestigationPayload(
            pods=pods,
            logs=logs,
            events=events,
            deployments=deployments,
            network=network,
        )


def start_investigation() -> InvestigationPayload:
    """Run an on-demand Kubernetes investigation."""

    return InvestigationService().run_investigation()
