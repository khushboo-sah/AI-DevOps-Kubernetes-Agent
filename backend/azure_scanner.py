"""Helpers for collecting Azure resource inventory via the Azure CLI."""

from __future__ import annotations

import json
import subprocess
from typing import Any


class AzureCliError(Exception):
    """Raised when an Azure CLI command cannot complete successfully."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _run_az_command(args: list[str], timeout_seconds: int = 60) -> Any:
    """Run an Azure CLI command and parse its JSON output."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise AzureCliError(
            "Azure CLI is not installed. Install Azure CLI and try again.",
            status_code=503,
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise AzureCliError(
            "Azure CLI command timed out. Check your Azure connection and try again.",
            status_code=504,
        ) from exc

    if result.returncode != 0:
        raise _map_az_error(result.stderr or result.stdout)

    output = result.stdout.strip()
    if not output:
        return []

    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise AzureCliError(
            "Azure CLI returned an invalid JSON response.",
            status_code=502,
        ) from exc


def _map_az_error(raw_message: str) -> AzureCliError:
    """Convert common Azure CLI failures into API-friendly messages."""
    message = raw_message.strip() or "Azure CLI command failed."
    lower_message = message.lower()

    if (
        "az login" in lower_message
        or "please run" in lower_message
        and "login" in lower_message
        or "not logged in" in lower_message
        or "login required" in lower_message
    ):
        return AzureCliError(
            "Azure CLI is not logged in. Run 'az login' and try again.",
            status_code=401,
        )

    if (
        "resource group" in lower_message
        and (
            "could not be found" in lower_message
            or "was not found" in lower_message
            or "does not exist" in lower_message
            or "notfound" in lower_message
        )
    ):
        return AzureCliError(
            "Resource group was not found. Verify the resource group name.",
            status_code=404,
        )

    return AzureCliError(message, status_code=400)


def list_resource_groups() -> list[dict[str, Any]]:
    """Return Azure resource groups visible to the current Azure CLI login."""
    groups = _run_az_command(["az", "group", "list", "-o", "json"])
    return [
        {
            "name": group.get("name"),
            "location": group.get("location"),
            "tags": group.get("tags") or {},
        }
        for group in groups
    ]


def list_resources(resource_group: str) -> list[dict[str, Any]]:
    """Return normalized Azure resources for a resource group."""
    resources = _run_az_command(
        ["az", "resource", "list", "--resource-group", resource_group, "-o", "json"]
    )
    return [_normalize_resource(resource) for resource in resources]


def _normalize_resource(resource: dict[str, Any]) -> dict[str, Any]:
    sku = resource.get("sku")

    return {
        "type": resource.get("type"),
        "name": resource.get("name"),
        "location": resource.get("location"),
        "sku": sku if sku is not None else None,
        "tags": resource.get("tags") or {},
    }
