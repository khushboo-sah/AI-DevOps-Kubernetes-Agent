"""Discover Kubernetes clusters from the local kubeconfig."""

from __future__ import annotations

import os
from pathlib import Path

from loguru import logger

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.cluster import ClusterContext, ClusterListResponse


class KubeconfigService:
    """Read cluster contexts available on the machine running the backend."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()

    def list_clusters(self) -> ClusterListResponse:
        """Return all kubectl contexts from the configured kubeconfig."""

        kubeconfig_path = self._resolve_kubeconfig_path()
        kubeconfig_found = bool(kubeconfig_path and Path(kubeconfig_path).is_file())

        if kubeconfig_path and not kubeconfig_found:
            return ClusterListResponse(
                kubeconfig_path=kubeconfig_path,
                kubeconfig_found=False,
                errors=[
                    f"Kubeconfig file not found at {kubeconfig_path}. "
                    "Set KUBECONFIG_PATH or mount ~/.kube when using Docker."
                ],
            )

        result, payload = self.executor.run_json(["config", "view", "-o", "json"])
        if not result.success or payload is None:
            return ClusterListResponse(
                kubeconfig_path=kubeconfig_path,
                kubeconfig_found=kubeconfig_found,
                errors=[result.error_message],
            )

        current_context = payload.get("current-context")
        contexts = self._parse_contexts(payload, current_context)

        logger.info("Discovered {} Kubernetes context(s)", len(contexts))
        return ClusterListResponse(
            kubeconfig_path=kubeconfig_path,
            kubeconfig_found=kubeconfig_found or bool(contexts),
            current_context=current_context,
            contexts=contexts,
        )

    def verify_context(self, context: str) -> tuple[bool, str | None]:
        """Check that a context exists and the API server is reachable."""

        clusters = self.list_clusters()
        if clusters.errors and not clusters.contexts:
            return False, clusters.errors[0]

        known = {item.name for item in clusters.contexts}
        if context not in known:
            return False, (
                f"Context '{context}' was not found in kubeconfig. "
                "Refresh the cluster list and choose a valid cluster."
            )

        executor = KubectlExecutor(context=context)
        result = executor.run(["cluster-info"], timeout_seconds=15)
        if result.success:
            return True, None

        return False, result.error_message

    def _resolve_kubeconfig_path(self) -> str | None:
        from app.core.config import get_settings

        settings = get_settings()
        if settings.kubeconfig_path:
            return settings.kubeconfig_path

        kubeconfig_env = os.getenv("KUBECONFIG")
        if kubeconfig_env:
            return kubeconfig_env.split(os.pathsep)[0]

        home_config = Path.home() / ".kube" / "config"
        if home_config.is_file():
            return str(home_config)

        return None

    def _parse_contexts(
        self,
        payload: dict,
        current_context: str | None,
    ) -> list[ClusterContext]:
        cluster_servers = {
            item.get("name"): item.get("cluster", {}).get("server")
            for item in payload.get("clusters", [])
            if item.get("name")
        }

        contexts: list[ClusterContext] = []
        for item in payload.get("contexts", []):
            context_name = item.get("name")
            context_data = item.get("context", {})
            if not context_name:
                continue

            cluster_name = context_data.get("cluster", "")
            contexts.append(
                ClusterContext(
                    name=context_name,
                    cluster=cluster_name,
                    user=context_data.get("user", ""),
                    namespace=context_data.get("namespace"),
                    cluster_server=cluster_servers.get(cluster_name),
                    is_current=context_name == current_context,
                )
            )

        return contexts
