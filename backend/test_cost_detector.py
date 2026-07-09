"""Tests for cost_detector rule-based checks and orchestration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from cost_detector import (
    CostDetectorError,
    _detect_rule_based_issues,
    detect_cost_issues,
)


class TestRuleBasedDetection(unittest.TestCase):
    def test_detects_over_provisioned_vm(self) -> None:
        resources = [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-large",
                "sku": {"name": "Standard_D8s_v3"},
                "tags": {"env": "prod"},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Potentially over-provisioned VM")
        self.assertEqual(findings[0]["severity"], "high")
        self.assertEqual(findings[0]["category"], "over_provisioning")

    def test_detects_non_prod_vm_sizing_issue(self) -> None:
        resources = [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-dev",
                "sku": {"name": "Standard_B2s"},
                "tags": {"env": "dev"},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Non-prod VM sizing review")
        self.assertEqual(findings[0]["severity"], "medium")

    def test_detects_public_ip(self) -> None:
        resources = [
            {
                "type": "Microsoft.Network/publicIPAddresses",
                "name": "pip-idle",
                "sku": None,
                "tags": {},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Public IP present")
        self.assertEqual(findings[0]["category"], "unused_or_idle")

    def test_detects_premium_storage_account(self) -> None:
        resources = [
            {
                "type": "Microsoft.Storage/storageAccounts",
                "name": "premiumstore",
                "sku": {"name": "Premium_LRS"},
                "tags": {},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Premium storage account")
        self.assertEqual(findings[0]["category"], "wrong_pricing_tier")

    def test_detects_higher_tier_app_service_plan(self) -> None:
        resources = [
            {
                "type": "Microsoft.Web/serverfarms",
                "name": "asp-prod",
                "sku": {"name": "P1v3"},
                "tags": {},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Higher-tier App Service plan")

    def test_returns_no_findings_for_small_app_service_plan(self) -> None:
        resources = [
            {
                "type": "Microsoft.Web/serverfarms",
                "name": "asp-free",
                "sku": {"name": "F1"},
                "tags": {},
            }
        ]

        findings = _detect_rule_based_issues(resources)

        self.assertEqual(findings, [])


class TestDetectCostIssues(unittest.TestCase):
    @patch("cost_detector.analyze_resources")
    def test_merges_rule_findings_with_ai_analysis(self, mock_analyze) -> None:
        mock_analyze.return_value = {
            "summary": "AI summary",
            "issues": [
                {
                    "title": "AI issue",
                    "description": "From OpenAI",
                    "severity": "high",
                    "resource_name": "vm-large",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "estimated_monthly_savings_usd": 100,
                    "fix_commands": ["az vm resize --size Standard_B2s"],
                }
            ],
            "estimated_total_savings_usd": 100,
            "fix_commands": ["az vm resize --size Standard_B2s"],
        }

        resources = [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-large",
                "sku": {"name": "Standard_D8s_v3"},
                "tags": {"env": "prod"},
            }
        ]

        result = detect_cost_issues("rg-demo", resources)

        self.assertEqual(result["summary"], "AI summary")
        self.assertEqual(result["resource_count"], 1)
        self.assertEqual(len(result["rule_based_findings"]), 1)
        self.assertEqual(result["issues"][0]["title"], "AI issue")
        mock_analyze.assert_called_once_with("rg-demo", resources)

    @patch("cost_detector.analyze_resources")
    def test_raises_cost_detector_error_when_ai_fails(self, mock_analyze) -> None:
        from ai_analyzer import AIAnalyzerError

        mock_analyze.side_effect = AIAnalyzerError("OpenAI failed", status_code=502)

        with self.assertRaises(CostDetectorError) as context:
            detect_cost_issues("rg-demo", [])

        self.assertEqual(context.exception.status_code, 502)
        self.assertEqual(context.exception.message, "OpenAI failed")


if __name__ == "__main__":
    unittest.main()
