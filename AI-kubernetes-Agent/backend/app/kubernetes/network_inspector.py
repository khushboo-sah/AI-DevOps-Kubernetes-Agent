"""Inspect Kubernetes services and endpoint wiring."""

from typing import Any

from app.kubernetes.kubectl_executor import KubectlExecutor
from app.models.investigation import NetworkInspectionResult, NetworkIssue


class NetworkInspector:
    """Check services, selectors, endpoints, and DNS-related events."""

    def __init__(self, executor: KubectlExecutor | None = None) -> None:
        self.executor = executor or KubectlExecutor()

    def inspect(self) -> NetworkInspectionResult:
        """Inspect service networking across all namespaces."""

        services_result, services_data = self.executor.run_json(
            ["get", "svc", "-A", "-o", "json"]
        )
        endpoints_result, endpoints_data = self.executor.run_json(
            ["get", "endpoints", "-A", "-o", "json"]
        )
        pods_result, pods_data = self.executor.run_json(["get", "pods", "-A", "-o", "json"])

        errors = [
            result.error_message
            for result in (services_result, endpoints_result, pods_result)
            if not result.success
        ]

        if services_data is None:
            return NetworkInspectionResult(healthy=False, errors=errors)

        services = services_data.get("items", [])
        endpoints_by_key = self._index_by_namespace_and_name(endpoints_data)
        pods_by_namespace = self._group_pods_by_namespace(pods_data)
        issues: list[NetworkIssue] = []

        for service in services:
            issues.extend(
                self._inspect_service(service, endpoints_by_key, pods_by_namespace)
            )

        issues.extend(self._collect_dns_event_issues())

        return NetworkInspectionResult(
            healthy=len(issues) == 0 and len(errors) == 0,
            services_checked=len(services),
            issues=issues,
            errors=errors,
        )

    def _inspect_service(
        self,
        service: dict[str, Any],
        endpoints_by_key: dict[tuple[str, str], dict[str, Any]],
        pods_by_namespace: dict[str, list[dict[str, Any]]],
    ) -> list[NetworkIssue]:
        metadata = service.get("metadata", {})
        spec = service.get("spec", {})
        namespace = metadata.get("namespace", "default")
        name = metadata.get("name", "unknown")
        service_type = spec.get("type", "ClusterIP")
        selector = spec.get("selector", {})

        if service_type == "ExternalName":
            return []

        issues: list[NetworkIssue] = []
        matching_pods = self._find_matching_pods(
            selector,
            pods_by_namespace.get(namespace, []),
        )

        if selector and not matching_pods:
            issues.append(
                NetworkIssue(
                    type="selector_mismatch",
                    namespace=namespace,
                    name=name,
                    message="Service selector does not match any pods",
                    details={"selector": selector},
                )
            )

        endpoint = endpoints_by_key.get((namespace, name))
        ready_addresses, not_ready_addresses = self._count_endpoint_addresses(endpoint)
        if selector and ready_addresses == 0:
            issue_type = "missing_endpoints"
            message = "Service has no ready endpoints"
            if not_ready_addresses > 0:
                issue_type = "no_ready_endpoints"
                message = "Service endpoints exist but none are ready"

            issues.append(
                NetworkIssue(
                    type=issue_type,
                    namespace=namespace,
                    name=name,
                    message=message,
                    details={
                        "selector": selector,
                        "matching_pods": len(matching_pods),
                        "not_ready_endpoints": not_ready_addresses,
                    },
                )
            )

        return issues

    def _collect_dns_event_issues(self) -> list[NetworkIssue]:
        result, data = self.executor.run_json(["get", "events", "-A", "-o", "json"])
        if not result.success or data is None:
            return []

        issues: list[NetworkIssue] = []
        for event in data.get("items", []):
            reason = event.get("reason", "")
            message = event.get("message", "")
            if "dns" not in f"{reason} {message}".lower():
                continue

            metadata = event.get("metadata", {})
            involved_object = event.get("involvedObject", {})
            issues.append(
                NetworkIssue(
                    type="dns_event",
                    namespace=metadata.get("namespace", "default"),
                    name=involved_object.get("name", metadata.get("name", "unknown")),
                    message=message,
                    details={"reason": reason},
                )
            )

        return issues

    def _index_by_namespace_and_name(
        self,
        data: dict[str, Any] | None,
    ) -> dict[tuple[str, str], dict[str, Any]]:
        if data is None:
            return {}

        indexed = {}
        for item in data.get("items", []):
            metadata = item.get("metadata", {})
            indexed[(metadata.get("namespace", "default"), metadata.get("name", ""))] = item
        return indexed

    def _group_pods_by_namespace(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        if data is None:
            return grouped

        for pod in data.get("items", []):
            namespace = pod.get("metadata", {}).get("namespace", "default")
            grouped.setdefault(namespace, []).append(pod)
        return grouped

    def _find_matching_pods(
        self,
        selector: dict[str, str],
        pods: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not selector:
            return []

        return [
            pod
            for pod in pods
            if self._labels_match(selector, pod.get("metadata", {}).get("labels", {}))
        ]

    def _labels_match(self, selector: dict[str, str], labels: dict[str, str]) -> bool:
        return all(labels.get(key) == value for key, value in selector.items())

    def _count_endpoint_addresses(
        self,
        endpoint: dict[str, Any] | None,
    ) -> tuple[int, int]:
        if endpoint is None:
            return 0, 0

        ready_addresses = 0
        not_ready_addresses = 0
        for subset in endpoint.get("subsets", []):
            ready_addresses += len(subset.get("addresses", []))
            not_ready_addresses += len(subset.get("notReadyAddresses", []))

        return ready_addresses, not_ready_addresses
