"""Tests for Prompt 1 FastAPI endpoints."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from main import AnalyzeRequest, analyze_resource_group, get_resource_groups


class TestMainEndpoints(unittest.TestCase):
    @patch("main.list_resource_groups")
    def test_get_resource_groups(self, mock_list_groups) -> None:
        mock_list_groups.return_value = [
            {"name": "rg-demo", "location": "eastus", "tags": {}}
        ]

        response = get_resource_groups()

        self.assertEqual(response["count"], 1)
        self.assertEqual(response["resource_groups"][0]["name"], "rg-demo")

    @patch("main.list_resources")
    def test_post_analyze_returns_structured_resources(self, mock_list_resources) -> None:
        mock_list_resources.return_value = [
            {
                "type": "Microsoft.Compute/virtualMachines",
                "name": "vm-demo",
                "location": "eastus",
                "sku": {"name": "Standard_B2s"},
                "tags": {"env": "dev"},
            }
        ]

        response = analyze_resource_group(AnalyzeRequest(resource_group="rg-demo"))

        self.assertEqual(response["resource_group"], "rg-demo")
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["resources"][0]["type"], "Microsoft.Compute/virtualMachines")
        self.assertNotIn("analysis", response)

    @patch("main.list_resources")
    def test_analyze_with_empty_resource_group_list(self, mock_list_resources) -> None:
        mock_list_resources.return_value = []

        response = analyze_resource_group(AnalyzeRequest(resource_group="rg-demo"))

        self.assertEqual(response["resource_group"], "rg-demo")
        self.assertEqual(response["count"], 0)
        self.assertEqual(response["resources"], [])


if __name__ == "__main__":
    unittest.main()
