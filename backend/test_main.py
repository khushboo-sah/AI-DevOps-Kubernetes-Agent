"""Tests for Prompt 2/3 analyze endpoint integration."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from main import AnalyzeRequest, analyze_resource_group


class TestAnalyzeWithAI(unittest.IsolatedAsyncioTestCase):
    @patch("main.save_analysis", new_callable=AsyncMock)
    @patch("main.progress_manager.send", new_callable=AsyncMock)
    @patch("main.analyze_resources")
    @patch("main.list_resources")
    async def test_post_analyze_returns_ai_analysis_and_stores_result(
        self,
        mock_list_resources,
        mock_analyze_resources,
        mock_send,
        mock_save_analysis,
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
        mock_save_analysis.return_value = 42

        response = await analyze_resource_group(
            AnalyzeRequest(resource_group="rg-demo", analysis_id="run-123"),
            user_id=7,
        )

        self.assertEqual(response["id"], 42)
        self.assertEqual(response["resource_group"], "rg-demo")
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["analysis"]["issues"][0]["severity"], "high")
        mock_save_analysis.assert_awaited_once()
        mock_send.assert_any_await("Analyzing costs with AI...")
        mock_send.assert_any_await("Analysis complete")


if __name__ == "__main__":
    unittest.main()
