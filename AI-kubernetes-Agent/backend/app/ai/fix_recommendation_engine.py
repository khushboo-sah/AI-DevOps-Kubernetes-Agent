"""Generate practical Kubernetes fix recommendations."""

from app.models.investigation import InvestigationPayload


class FixRecommendationEngine:
    """Produce beginner-friendly remediation guidance."""

    def recommend(self, root_cause: str, investigation: InvestigationPayload) -> tuple[str, list[str], str]:
        """Return fix text, kubectl commands, and prevention guidance."""

        root_cause_lower = root_cause.lower()
        target = self._first_workload_name(investigation)
        namespace = self._first_namespace(investigation)

        if "environment variable" in root_cause_lower:
            return (
                "Add the missing environment variable to the affected deployment and restart the rollout.",
                [
                    f"kubectl describe deployment {target} -n {namespace}",
                    f"kubectl edit deployment {target} -n {namespace}",
                    f"kubectl rollout restart deployment/{target} -n {namespace}",
                ],
                "Define required environment variables through ConfigMaps or Secrets and validate them during application startup.",
            )

        if "image" in root_cause_lower and "pull" in root_cause_lower:
            return (
                "Fix the image name, tag, registry credentials, or imagePullSecret for the affected workload.",
                [
                    f"kubectl describe pod {self._first_pod_name(investigation)} -n {namespace}",
                    f"kubectl edit deployment {target} -n {namespace}",
                    f"kubectl rollout status deployment/{target} -n {namespace}",
                ],
                "Use immutable image tags and verify registry credentials before deploying.",
            )

        if "memory" in root_cause_lower or "oomkilled" in root_cause_lower:
            return (
                "Increase the container memory limit or reduce application memory usage.",
                [
                    f"kubectl describe pod {self._first_pod_name(investigation)} -n {namespace}",
                    f"kubectl edit deployment {target} -n {namespace}",
                    f"kubectl rollout restart deployment/{target} -n {namespace}",
                ],
                "Set realistic resource requests and limits based on observed application memory usage.",
            )

        if "not being scheduled" in root_cause_lower:
            return (
                "Review scheduling events, resource requests, node capacity, taints, and affinity rules.",
                [
                    "kubectl get nodes",
                    f"kubectl describe pod {self._first_pod_name(investigation)} -n {namespace}",
                    "kubectl get events -A --sort-by=.lastTimestamp",
                ],
                "Add capacity checks and validate scheduling constraints before rollout.",
            )

        if "service selector" in root_cause_lower:
            service_name = self._first_network_issue_name(investigation)
            return (
                "Update the service selector or pod labels so the service points at the intended pods.",
                [
                    f"kubectl describe svc {service_name} -n {namespace}",
                    f"kubectl get pods -n {namespace} --show-labels",
                    f"kubectl edit svc {service_name} -n {namespace}",
                ],
                "Keep service selectors and pod labels documented together in deployment manifests.",
            )

        if "no ready endpoints" in root_cause_lower or "no ready endpoints" in self._network_messages(investigation):
            service_name = self._first_network_issue_name(investigation)
            return (
                "Check why backing pods are not ready and fix readiness probes or pod health.",
                [
                    f"kubectl describe svc {service_name} -n {namespace}",
                    f"kubectl get endpoints {service_name} -n {namespace}",
                    f"kubectl get pods -n {namespace} -o wide",
                ],
                "Add readiness probe monitoring so endpoint loss is detected before users are impacted.",
            )

        if "kubectl access" in root_cause_lower:
            return (
                "Install kubectl and configure KUBECONFIG_PATH so the backend can access the target cluster.",
                [
                    "kubectl config current-context",
                    "kubectl get pods -A",
                ],
                "Validate cluster access during backend startup or deployment health checks.",
            )

        return (
            "Review the collected pod, event, deployment, and network evidence to identify the failing component.",
            [
                "kubectl get pods -A",
                "kubectl get events -A --sort-by=.lastTimestamp",
                "kubectl get deployments -A",
            ],
            "Add deployment checks and alerting for pods, events, deployments, and service endpoints.",
        )

    def _first_workload_name(self, investigation: InvestigationPayload) -> str:
        if investigation.deployments.unhealthy_deployments:
            return investigation.deployments.unhealthy_deployments[0].name
        return self._first_pod_name(investigation)

    def _first_pod_name(self, investigation: InvestigationPayload) -> str:
        if investigation.pods.problematic_pods:
            return investigation.pods.problematic_pods[0].name
        return "<pod-name>"

    def _first_namespace(self, investigation: InvestigationPayload) -> str:
        if investigation.pods.problematic_pods:
            return investigation.pods.problematic_pods[0].namespace
        if investigation.deployments.unhealthy_deployments:
            return investigation.deployments.unhealthy_deployments[0].namespace
        if investigation.network.issues:
            return investigation.network.issues[0].namespace
        return "default"

    def _first_network_issue_name(self, investigation: InvestigationPayload) -> str:
        if investigation.network.issues:
            return investigation.network.issues[0].name
        return "<service-name>"

    def _network_messages(self, investigation: InvestigationPayload) -> str:
        return " ".join(issue.message.lower() for issue in investigation.network.issues)
