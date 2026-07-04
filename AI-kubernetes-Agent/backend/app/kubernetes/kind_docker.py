"""kind cluster helpers when the backend runs inside Docker."""

from __future__ import annotations

import os


def is_kind_docker_mode() -> bool:
    """Return True when the backend should reach kind via the Docker network."""

    return os.getenv("KUBE_KIND_DOCKER_NETWORK", "").lower() in {"1", "true", "yes"}


def kind_control_plane_host(context: str) -> str | None:
    """Map a kind kubectl context to its control-plane container hostname.

    Examples:
        kind-kind -> kind-control-plane
        kind-dev  -> dev-control-plane
    """

    if not context.startswith("kind-"):
        return None

    cluster_name = context.removeprefix("kind-")
    if not cluster_name:
        return None

    return f"{cluster_name}-control-plane"


def resolve_api_server(context: str | None) -> str | None:
    """Return an in-Docker API server URL for kind contexts."""

    if not context or not is_kind_docker_mode():
        return None

    host = kind_control_plane_host(context)
    if not host:
        return None

    return f"https://{host}:6443"
