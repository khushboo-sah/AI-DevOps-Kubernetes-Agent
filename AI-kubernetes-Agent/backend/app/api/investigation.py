"""Kubernetes investigation endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import AuthenticatedUser, require_authenticated_user
from app.core.kubernetes_errors import (
    friendly_kubectl_error,
    friendly_openrouter_error,
    summarize_investigation_errors,
)
from app.kubernetes.kubeconfig_service import KubeconfigService
from app.models.investigation import (
    Diagnosis,
    InvestigationPayload,
    InvestigationRequest,
    InvestigationResponse,
)
from app.services.investigation_service import InvestigationService

router = APIRouter(tags=["investigation"])


@router.post("/investigate", response_model=InvestigationResponse)
def investigate_cluster(
    request: InvestigationRequest | None = None,
    _: AuthenticatedUser = Depends(require_authenticated_user),
) -> InvestigationResponse:
    """Collect Kubernetes evidence and return an AI-assisted diagnosis."""

    context = request.context if request else None
    kubeconfig_service = KubeconfigService()

    if context:
        reachable, error_message = kubeconfig_service.verify_context(context)
        if not reachable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=friendly_kubectl_error(error_message or "Cluster is unreachable"),
            )

    try:
        service = InvestigationService(context=context)
        investigation = service.run_investigation()
        diagnosis = service.diagnose_investigation(investigation)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Investigation failed unexpectedly. Check backend logs for details.",
        ) from exc

    collector_errors = _collect_errors(investigation)
    response_errors: list[str] = []

    if diagnosis.errors:
        response_errors.extend(
            friendly_openrouter_error(item) for item in diagnosis.errors
        )

    if _all_collectors_failed(investigation):
        summary = summarize_investigation_errors(collector_errors) or (
            "Unable to collect Kubernetes evidence from the selected cluster."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=summary,
        )

    if _is_cluster_healthy(investigation):
        diagnosis = _build_healthy_diagnosis(investigation.cluster_context)
        return InvestigationResponse(
            status="healthy",
            cluster_context=investigation.cluster_context,
            message="No critical Kubernetes issues detected. Cluster appears healthy.",
            investigation=investigation,
            diagnosis=diagnosis,
            errors=response_errors,
        )

    response_status = "success"
    if collector_errors:
        response_status = "partial"
        response_errors.extend(collector_errors)

    return InvestigationResponse(
        status=response_status,
        cluster_context=investigation.cluster_context,
        investigation=investigation,
        diagnosis=diagnosis,
        errors=response_errors,
    )


def _collect_errors(investigation: InvestigationPayload) -> list[str]:
    return [
        *investigation.pods.errors,
        *investigation.logs.errors,
        *investigation.events.errors,
        *investigation.deployments.errors,
        *investigation.network.errors,
    ]


def _all_collectors_failed(investigation: InvestigationPayload) -> bool:
    critical_sections = (
        investigation.pods,
        investigation.events,
        investigation.deployments,
        investigation.network,
    )
    return all(section.errors for section in critical_sections)


def _is_cluster_healthy(investigation: InvestigationPayload) -> bool:
    has_workload_issues = bool(
        investigation.pods.problematic_pods
        or investigation.deployments.unhealthy_deployments
        or investigation.events.findings
        or investigation.network.issues
    )
    if has_workload_issues:
        return False

    collector_errors = _collect_errors(investigation)
    return not collector_errors


def _build_healthy_diagnosis(cluster_context: str | None) -> Diagnosis:
    cluster_label = cluster_context or "the selected cluster"
    return Diagnosis(
        root_cause="No critical Kubernetes issues detected.",
        explanation=(
            f"{cluster_label} appears healthy. Pods, deployments, events, and "
            "networking checks did not surface critical failures."
        ),
        fix="No immediate action required. Continue monitoring cluster health.",
        kubectl_command="kubectl get pods -A",
        kubectl_commands=[
            "kubectl get pods -A",
            "kubectl get events -A --sort-by=.lastTimestamp",
        ],
        prevention_recommendation=(
            "Keep alerts on CrashLoopBackOff, ImagePullBackOff, failed deployments, "
            "and services without ready endpoints."
        ),
        confidence=88,
        confidence_reasoning=[
            "No problematic pods were detected.",
            "No unhealthy deployments or critical network issues were found.",
        ],
        source="fallback",
    )
