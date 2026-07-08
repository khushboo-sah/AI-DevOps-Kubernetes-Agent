"""Kubernetes cluster discovery endpoints."""

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, require_authenticated_user
from app.kubernetes.kubeconfig_service import KubeconfigService
from app.models.cluster import ClusterListResponse

router = APIRouter(tags=["clusters"])


@router.get("/clusters", response_model=ClusterListResponse)
def list_clusters(
    _: AuthenticatedUser = Depends(require_authenticated_user),
) -> ClusterListResponse:
    """List Kubernetes clusters available in the local kubeconfig."""

    return KubeconfigService().list_clusters()
