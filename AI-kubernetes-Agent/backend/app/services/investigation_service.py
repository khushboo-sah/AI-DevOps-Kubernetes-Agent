"""Orchestrate Kubernetes evidence collection."""

from loguru import logger

from app.ai.agent import AIKubernetesAgent
from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.kubectl_executor import KubectlExecutor
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.pod_inspector import PodInspector
from app.models.investigation import Diagnosis, InvestigationPayload


class InvestigationService:
    """Run the Kubernetes investigation workflow."""

    def __init__(
        self,
        executor: KubectlExecutor | None = None,
        context: str | None = None,
    ) -> None:
        self.context = context
        self.executor = executor or KubectlExecutor(context=context)
        self.pod_inspector = PodInspector(self.executor)
        self.logs_collector = LogsCollector(self.executor)
        self.events_analyzer = EventsAnalyzer(self.executor)
        self.deployment_inspector = DeploymentInspector(self.executor)
        self.network_inspector = NetworkInspector(self.executor)
        self.ai_agent = AIKubernetesAgent()

    def run_investigation(self) -> InvestigationPayload:
        """Collect Kubernetes troubleshooting evidence in a predictable order."""

        logger.info(
            "Starting Kubernetes investigation for context {}",
            self.context or "default",
        )
        pods = self.pod_inspector.inspect()
        logs = self.logs_collector.collect(pods.problematic_pods)
        events = self.events_analyzer.analyze()
        deployments = self.deployment_inspector.inspect()
        network = self.network_inspector.inspect()
        logger.info("Finished Kubernetes investigation")

        return InvestigationPayload(
            cluster_context=self.context,
            pods=pods,
            logs=logs,
            events=events,
            deployments=deployments,
            network=network,
        )

    def diagnose_investigation(
        self,
        investigation: InvestigationPayload,
    ) -> Diagnosis:
        """Generate a Senior SRE-style diagnosis from collected evidence."""

        logger.info("Starting AI Kubernetes diagnosis")
        diagnosis = self.ai_agent.diagnose(investigation)
        logger.info("Finished AI Kubernetes diagnosis with source {}", diagnosis.source)
        return diagnosis


def start_investigation() -> InvestigationPayload:
    """Run an on-demand Kubernetes investigation."""

    return InvestigationService().run_investigation()
