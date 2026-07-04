"""Beginner-friendly Kubernetes error messages."""

from typing import Sequence


def friendly_kubectl_error(stderr: str, return_code: int | None = None) -> str:
    """Map raw kubectl output to a helpful message for the UI."""

    text = (stderr or "").lower()

    if "command not found" in text or return_code == 127:
        return (
            "kubectl is not installed or not available on the server PATH. "
            "Install kubectl and restart the backend."
        )

    if "timed out" in text or return_code == 124:
        return (
            "The Kubernetes API did not respond in time. "
            "The cluster may be unreachable or overloaded."
        )

    if "no configuration has been provided" in text or "kubeconfig" in text and "not found" in text:
        return (
            "No kubeconfig file was found.\n\n"
            "Please verify:\n"
            "- kubeconfig path is set (KUBECONFIG_PATH or KUBECONFIG)\n"
            "- the file exists on the machine running the backend\n"
            "- Docker mounts your ~/.kube directory if using containers"
        )

    if "connection refused" in text or "unable to connect" in text or "dial tcp" in text:
        return (
            "Unable to connect to the Kubernetes cluster.\n\n"
            "Please verify:\n"
            "- the cluster is running\n"
            "- kubeconfig points to the correct API server\n"
            "- VPN or network access to the cluster is available"
        )

    if "unauthorized" in text or "forbidden" in text or "permission denied" in text:
        return (
            "kubectl does not have permission to access this cluster.\n\n"
            "Please verify:\n"
            "- your kubeconfig credentials are valid\n"
            "- your user or service account has RBAC permissions\n"
            "- the selected context is correct"
        )

    if "context" in text and "does not exist" in text:
        return (
            "The selected Kubernetes context was not found in your kubeconfig. "
            "Refresh the cluster list and choose a valid context."
        )

    if "the connection to the server" in text and "was refused" in text:
        return (
            "Unable to connect to the Kubernetes API server. "
            "Check that the cluster is running and your kubeconfig is up to date."
        )

    cleaned = stderr.strip() if stderr else "kubectl command failed"
    return cleaned


def friendly_openrouter_error(error: str) -> str:
    """Map OpenRouter / LLM errors to a helpful message."""

    text = error.lower()

    if "not configured" in text or "openrouter_api_key" in text:
        return (
            "AI reasoning is unavailable because OPENROUTER_API_KEY is not configured. "
            "The agent will use rule-based diagnosis instead."
        )

    if "timeout" in text or "timed out" in text:
        return (
            "AI reasoning timed out. The agent used rule-based diagnosis instead. "
            "Try again or check your OpenRouter API connectivity."
        )

    if "rate limit" in text or "429" in text:
        return (
            "AI reasoning was rate limited. The agent used rule-based diagnosis instead. "
            "Wait a moment and try again."
        )

    return f"AI reasoning failed: {error}. Rule-based diagnosis was used instead."


def summarize_investigation_errors(errors: Sequence[str]) -> str | None:
    """Return a single friendly message when investigation collectors fail."""

    if not errors:
        return None

    combined = " ".join(errors).lower()

    if any(
        phrase in combined
        for phrase in (
            "kubeconfig",
            "no configuration",
            "connection refused",
            "unable to connect",
            "dial tcp",
        )
    ):
        return (
            "Unable to connect to the Kubernetes cluster.\n\n"
            "Please verify:\n"
            "- kubeconfig path\n"
            "- cluster access\n"
            "- kubectl permissions"
        )

    if "timed out" in combined:
        return (
            "Kubernetes investigation timed out.\n\n"
            "Please verify:\n"
            "- cluster responsiveness\n"
            "- network connectivity\n"
            "- try a smaller or less busy cluster"
        )

    return errors[0]
