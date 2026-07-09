"""Tests for azure_scanner Azure CLI integration."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from azure_scanner import (
    AzureCliError,
    _normalize_resource,
    list_resource_groups,
    list_resources,
)


class TestAzureScanner(unittest.TestCase):
    @patch("azure_scanner.subprocess.run")
    def test_list_resource_groups_parses_json(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "name": "rg-demo",
                        "location": "eastus",
                        "tags": {"env": "dev"},
                    }
                ]
            ),
            stderr="",
        )

        groups = list_resource_groups()

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["name"], "rg-demo")
        self.assertEqual(groups[0]["location"], "eastus")
        self.assertEqual(groups[0]["tags"], {"env": "dev"})
        mock_run.assert_called_once_with(
            ["az", "group", "list", "-o", "json"],
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )

    @patch("azure_scanner.subprocess.run")
    def test_list_resources_returns_structured_fields(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "type": "Microsoft.Compute/virtualMachines",
                        "name": "vm-demo",
                        "location": "eastus",
                        "sku": {"name": "Standard_B2s"},
                        "tags": {"owner": "team-a"},
                    }
                ]
            ),
            stderr="",
        )

        resources = list_resources("rg-demo")

        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["type"], "Microsoft.Compute/virtualMachines")
        self.assertEqual(resources[0]["name"], "vm-demo")
        self.assertEqual(resources[0]["location"], "eastus")
        self.assertEqual(resources[0]["sku"], {"name": "Standard_B2s"})
        self.assertEqual(resources[0]["tags"], {"owner": "team-a"})

    def test_normalize_resource_includes_required_fields(self) -> None:
        normalized = _normalize_resource(
            {
                "type": "Microsoft.Storage/storageAccounts",
                "name": "store1",
                "location": "westus",
                "sku": None,
                "tags": None,
            }
        )

        self.assertEqual(normalized["type"], "Microsoft.Storage/storageAccounts")
        self.assertEqual(normalized["name"], "store1")
        self.assertEqual(normalized["location"], "westus")
        self.assertIsNone(normalized["sku"])
        self.assertEqual(normalized["tags"], {})

    @patch("azure_scanner.subprocess.run", side_effect=FileNotFoundError)
    def test_raises_when_azure_cli_not_installed(self, _mock_run: MagicMock) -> None:
        with self.assertRaises(AzureCliError) as context:
            list_resource_groups()

        self.assertEqual(context.exception.status_code, 503)
        self.assertIn("not installed", context.exception.message)

    @patch("azure_scanner.subprocess.run")
    def test_raises_when_not_logged_in(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Please run 'az login' to setup account.",
        )

        with self.assertRaises(AzureCliError) as context:
            list_resources("rg-demo")

        self.assertEqual(context.exception.status_code, 401)

    @patch("azure_scanner.subprocess.run")
    def test_raises_when_resource_group_not_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Resource group 'missing-rg' could not be found.",
        )

        with self.assertRaises(AzureCliError) as context:
            list_resources("missing-rg")

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
