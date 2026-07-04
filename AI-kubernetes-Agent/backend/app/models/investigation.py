"""Models for Kubernetes investigation evidence."""

from typing import Any

from pydantic import BaseModel, Field


class PodIssue(BaseModel):
    """A pod that appears unhealthy or stuck."""

    name: str
    namespace: str
    status: str
    reason: str | None = None
    containers: list[str] = Field(default_factory=list)


class PodInspectionResult(BaseModel):
    """Pod inspection summary."""

    healthy: bool
    checked_count: int = 0
    problematic_pods: list[PodIssue] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class PodLogSummary(BaseModel):
    """Concise log findings for one pod."""

    name: str
    namespace: str
    findings: list[str] = Field(default_factory=list)
    error: str | None = None


class LogsCollectionResult(BaseModel):
    """Log collection summary for problematic pods."""

    collected_count: int = 0
    logs: list[PodLogSummary] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class EventFinding(BaseModel):
    """A Kubernetes event that may explain a failure."""

    namespace: str
    reason: str
    message: str
    involved_object_kind: str | None = None
    involved_object_name: str | None = None
    count: int | None = None
    last_timestamp: str | None = None


class EventsAnalysisResult(BaseModel):
    """Kubernetes events analysis summary."""

    healthy: bool
    findings: list[EventFinding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class DeploymentCondition(BaseModel):
    """Deployment condition details from Kubernetes status."""

    type: str
    status: str
    reason: str | None = None
    message: str | None = None


class DeploymentIssue(BaseModel):
    """Deployment that appears unavailable or degraded."""

    name: str
    namespace: str
    desired_replicas: int
    available_replicas: int
    unavailable_replicas: int
    conditions: list[DeploymentCondition] = Field(default_factory=list)


class DeploymentInspectionResult(BaseModel):
    """Deployment inspection summary."""

    healthy: bool
    checked_count: int = 0
    unhealthy_deployments: list[DeploymentIssue] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class NetworkIssue(BaseModel):
    """Service or endpoint issue that may affect networking."""

    type: str
    namespace: str
    name: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class NetworkInspectionResult(BaseModel):
    """Service and endpoint inspection summary."""

    healthy: bool
    services_checked: int = 0
    issues: list[NetworkIssue] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class InvestigationPayload(BaseModel):
    """All evidence collected during a Kubernetes investigation."""

    pods: PodInspectionResult
    logs: LogsCollectionResult
    events: EventsAnalysisResult
    deployments: DeploymentInspectionResult
    network: NetworkInspectionResult


class Diagnosis(BaseModel):
    """Senior SRE-style diagnosis generated from investigation evidence."""

    root_cause: str
    explanation: str
    fix: str
    kubectl_command: str
    kubectl_commands: list[str] = Field(default_factory=list)
    prevention_recommendation: str
    confidence: int = Field(ge=0, le=100)
    confidence_reasoning: list[str] = Field(default_factory=list)
    source: str = "llm"
    errors: list[str] = Field(default_factory=list)


class InvestigationResponse(BaseModel):
    """API response for POST /investigate."""

    status: str
    investigation: InvestigationPayload
    diagnosis: Diagnosis
