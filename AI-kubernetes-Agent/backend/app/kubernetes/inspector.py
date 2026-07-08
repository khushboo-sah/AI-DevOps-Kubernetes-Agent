"""Convenience functions for Kubernetes investigation components.

These functions keep the early placeholder import path usable while delegating
to the concrete kubectl-based inspectors.
"""

from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.pod_inspector import PodInspector
from app.models.investigation import (
    DeploymentInspectionResult,
    EventsAnalysisResult,
    LogsCollectionResult,
    NetworkInspectionResult,
    PodInspectionResult,
)


def inspect_pods() -> PodInspectionResult:
    """Inspect pod health across all namespaces."""

    return PodInspector().inspect()


def collect_logs(pods: PodInspectionResult) -> LogsCollectionResult:
    """Collect concise logs for problematic pods."""

    return LogsCollector().collect(pods.problematic_pods)


def inspect_events() -> EventsAnalysisResult:
    """Analyze Kubernetes events across all namespaces."""

    return EventsAnalyzer().analyze()


def inspect_deployments() -> DeploymentInspectionResult:
    """Inspect deployment health across all namespaces."""

    return DeploymentInspector().inspect()


def inspect_network() -> NetworkInspectionResult:
    """Inspect services and endpoints across all namespaces."""

    return NetworkInspector().inspect()
