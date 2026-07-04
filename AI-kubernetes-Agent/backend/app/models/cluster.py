"""Models for Kubernetes cluster / kubeconfig discovery."""

from pydantic import BaseModel, Field


class ClusterContext(BaseModel):
    """A kubectl context from the local kubeconfig."""

    name: str
    cluster: str
    user: str
    namespace: str | None = None
    cluster_server: str | None = None
    is_current: bool = False


class ClusterListResponse(BaseModel):
    """API response for GET /clusters."""

    kubeconfig_path: str | None = None
    kubeconfig_found: bool
    current_context: str | None = None
    contexts: list[ClusterContext] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
