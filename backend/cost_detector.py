"""Orchestrates Azure cost detection using scanner data and AI analysis."""

from __future__ import annotations

from typing import Any

try:
    from ai_analyzer import AIAnalyzerError, analyze_resources
except ModuleNotFoundError:
    from .ai_analyzer import AIAnalyzerError, analyze_resources


class CostDetectorError(AIAnalyzerError):
    """Raised when cost detection cannot be completed."""


LARGE_VM_PREFIXES = ("Standard_D", "Standard_E", "Standard_F", "Standard_M")
PREMIUM_SKU_MARKERS = ("Premium", "P1", "P2", "P3", "P4", "P5")


def detect_cost_issues(
    resource_group: str, resources: list[dict[str, Any]]
) -> dict[str, Any]:
    """Detect cost issues in scanned Azure resources."""
    rule_based_findings = _detect_rule_based_issues(resources)

    try:
        ai_analysis = analyze_resources(resource_group, resources)
    except AIAnalyzerError as exc:
        raise CostDetectorError(exc.message, status_code=exc.status_code) from exc

    return {
        **ai_analysis,
        "rule_based_findings": rule_based_findings,
        "resource_count": len(resources),
    }


def _detect_rule_based_issues(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply lightweight heuristics before AI analysis."""
    findings: list[dict[str, Any]] = []

    for resource in resources:
        resource_type = resource.get("type") or ""
        resource_name = resource.get("name") or "unknown"
        sku = resource.get("sku") or {}
        sku_name = sku.get("name", "") if isinstance(sku, dict) else str(sku)
        tags = resource.get("tags") or {}

        if "Microsoft.Compute/virtualMachines" in resource_type:
            findings.extend(
                _check_virtual_machine(resource_name, sku_name, tags)
            )
        elif "Microsoft.Network/publicIPAddresses" in resource_type:
            findings.append(
                {
                    "title": "Public IP present",
                    "description": (
                        f"Public IP '{resource_name}' may incur charges even when idle."
                    ),
                    "severity": "medium",
                    "resource_name": resource_name,
                    "resource_type": resource_type,
                    "category": "unused_or_idle",
                }
            )
        elif "Microsoft.Storage/storageAccounts" in resource_type:
            findings.extend(
                _check_storage_account(resource_name, resource_type, sku_name)
            )
        elif "Microsoft.Web/serverfarms" in resource_type:
            findings.extend(
                _check_app_service_plan(resource_name, resource_type, sku_name)
            )

    return findings


def _check_virtual_machine(
    resource_name: str, sku_name: str, tags: dict[str, Any]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if any(sku_name.startswith(prefix) for prefix in LARGE_VM_PREFIXES):
        findings.append(
            {
                "title": "Potentially over-provisioned VM",
                "description": (
                    f"VM '{resource_name}' uses SKU '{sku_name}', which may be "
                    "larger than needed for non-production workloads."
                ),
                "severity": "high",
                "resource_name": resource_name,
                "resource_type": "Microsoft.Compute/virtualMachines",
                "category": "over_provisioning",
            }
        )

    if tags.get("env", "").lower() in {"dev", "test", "sandbox"} and sku_name:
        findings.append(
            {
                "title": "Non-prod VM sizing review",
                "description": (
                    f"VM '{resource_name}' is tagged as non-production but uses "
                    f"SKU '{sku_name}'."
                ),
                "severity": "medium",
                "resource_name": resource_name,
                "resource_type": "Microsoft.Compute/virtualMachines",
                "category": "misconfiguration",
            }
        )

    return findings


def _check_storage_account(
    resource_name: str, resource_type: str, sku_name: str
) -> list[dict[str, Any]]:
    if not any(marker in sku_name for marker in PREMIUM_SKU_MARKERS):
        return []

    return [
        {
            "title": "Premium storage account",
            "description": (
                f"Storage account '{resource_name}' uses premium tier SKU "
                f"'{sku_name}', which is more expensive than standard tiers."
            ),
            "severity": "medium",
            "resource_name": resource_name,
            "resource_type": resource_type,
            "category": "wrong_pricing_tier",
        }
    ]


def _check_app_service_plan(
    resource_name: str, resource_type: str, sku_name: str
) -> list[dict[str, Any]]:
    if not sku_name or sku_name in {"F1", "D1", "B1", "B2", "B3"}:
        return []

    return [
        {
            "title": "Higher-tier App Service plan",
            "description": (
                f"App Service plan '{resource_name}' uses SKU '{sku_name}'. "
                "Review whether a lower tier can meet workload needs."
            ),
            "severity": "medium",
            "resource_name": resource_name,
            "resource_type": resource_type,
            "category": "wrong_pricing_tier",
        }
    ]
