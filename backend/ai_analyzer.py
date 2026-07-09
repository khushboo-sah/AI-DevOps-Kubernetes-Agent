"""OpenAI-powered Azure cost analysis."""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

Severity = Literal["high", "medium", "low"]


class AIAnalyzerError(Exception):
    """Raised when AI cost analysis cannot be completed."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def analyze_resources(
    resource_group: str, resources: list[dict[str, Any]]
) -> dict[str, Any]:
    """Analyze Azure resources for cost optimization opportunities."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIAnalyzerError(
            "OPENAI_API_KEY is not configured. Add it to your .env file.",
            status_code=503,
        )

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(resource_group, resources)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )
    except RateLimitError as exc:
        raise AIAnalyzerError(
            "OpenAI rate limit exceeded. Try again in a moment.",
            status_code=429,
        ) from exc
    except APIConnectionError as exc:
        raise AIAnalyzerError(
            "Unable to connect to OpenAI API. Check your network and try again.",
            status_code=502,
        ) from exc
    except APIStatusError as exc:
        raise AIAnalyzerError(
            f"OpenAI API request failed: {exc.message}",
            status_code=502,
        ) from exc

    content = response.choices[0].message.content
    if not content:
        raise AIAnalyzerError(
            "OpenAI returned an empty analysis response.",
            status_code=502,
        )

    try:
        analysis = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIAnalyzerError(
            "OpenAI returned an invalid JSON analysis response.",
            status_code=502,
        ) from exc

    return _normalize_analysis(analysis)


def _system_prompt() -> str:
    return (
        "You are an Azure FinOps expert. Analyze Azure resource inventories for "
        "cost waste and optimization opportunities. Return only valid JSON with "
        "this schema:\n"
        "{\n"
        '  "summary": "string",\n'
        '  "issues": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "description": "string",\n'
        '      "severity": "high|medium|low",\n'
        '      "resource_name": "string",\n'
        '      "resource_type": "string",\n'
        '      "estimated_monthly_savings_usd": number,\n'
        '      "fix_commands": ["az ..."]\n'
        "    }\n"
        "  ],\n"
        '  "estimated_total_savings_usd": number,\n'
        '  "fix_commands": ["az ..."]\n'
        "}\n"
        "Focus on over-provisioning, unused or idle resources, misconfigurations, "
        "wrong pricing tiers, storage and logging costs, and reserved instance "
        "opportunities. Use realistic savings estimates. Provide actionable Azure "
        "CLI commands. If no issues are found, return an empty issues array and "
        "explain that in the summary."
    )


def _build_prompt(resource_group: str, resources: list[dict[str, Any]]) -> str:
    resource_payload = json.dumps(resources, indent=2)
    return (
        f"Analyze the following Azure resources in resource group '{resource_group}' "
        "for cost optimization:\n\n"
        f"{resource_payload}\n\n"
        "Identify over-provisioned resources, unused or idle resources, "
        "misconfigurations, wrong pricing tiers, and other cost optimization "
        "opportunities."
    )


def _normalize_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    issues = analysis.get("issues") or []
    normalized_issues: list[dict[str, Any]] = []

    for issue in issues:
        severity = str(issue.get("severity", "medium")).lower()
        if severity not in {"high", "medium", "low"}:
            severity = "medium"

        normalized_issues.append(
            {
                "title": issue.get("title", "Untitled issue"),
                "description": issue.get("description", ""),
                "severity": severity,
                "resource_name": issue.get("resource_name"),
                "resource_type": issue.get("resource_type"),
                "estimated_monthly_savings_usd": issue.get(
                    "estimated_monthly_savings_usd", 0
                ),
                "fix_commands": issue.get("fix_commands") or [],
            }
        )

    return {
        "summary": analysis.get("summary", "No summary provided."),
        "issues": normalized_issues,
        "estimated_total_savings_usd": analysis.get("estimated_total_savings_usd", 0),
        "fix_commands": analysis.get("fix_commands") or [],
    }
