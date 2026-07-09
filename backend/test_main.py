"""Tests for Prompt 2 analyze endpoint with AI integration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from main import AnalyzeRequest, analyze_resource_group


class TestAnalyzeWithAI(unittest.TestCase):
    @patch("main.analyze_resources")
    @patch("main.list_resources")
    def test_post_analyze_returns_ai_analysis(
        self, mock_list_resources, mock_analyze_resources
    ) -> None:
        mock_list_resources.return_value = [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-demo",
                "location": "eastus",
                "sku": {"name": "Standard_D8s_v3"},
                "tags": {"env": "dev"},
            }
        ]
        mock_analyze_resources.return_value = {
            "summary": "VM appears over-provisioned.",
            "issues": [
                {
                    "title": "Over-provisioned VM",
                    "description": "Consider a smaller SKU.",
                    "severity": "high",
                    "resource_name": "vm-demo",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "estimated_monthly_savings_usd": 120,
                    "fix_commands": [
                        "az vm resize --resource-group rg-demo --name vm-demo --size Standard_B2s"
                    ],
                }
            ],
            "estimated_total_savings_usd": 120,
            "fix_commands": [
                "az vm resize --resource-group rg-demo --name vm-demo --size Standard_B2s"
            ],
        }

        response = analyze_resource_group(AnalyzeRequest(resource_group="rg-demo"))

        self.assertEqual(response["resource_group"], "rg-demo")
        self.assertEqual(response["count"], 1)
        self.assertIn("analysis", response)
        self.assertEqual(response["analysis"]["issues"][0]["severity"], "high")
        mock_list_resources.assert_called_once_with("rg-demo")
        mock_analyze_resources.assert_called_once_with(
            "rg-demo", mock_list_resources.return_value
        )


if __name__ == "__main__":
    unittest.main()
