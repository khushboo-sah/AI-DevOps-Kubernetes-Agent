"""AI Kubernetes Agent orchestration.

The agent first tries OpenRouter for Senior SRE-style reasoning. If the API key
is missing or the API fails, it falls back to deterministic local heuristics so
the backend still returns a useful diagnosis.
"""

import json
from typing import Any

from loguru import logger
from pydantic import ValidationError

from app.ai.confidence_engine import ConfidenceEngine
from app.ai.fix_recommendation_engine import FixRecommendationEngine
from app.ai.llm_client import OpenRouterClient
from app.ai.prompt_builder import PromptBuilder
from app.ai.root_cause_analyzer import RootCauseAnalyzer
from app.models.investigation import Diagnosis, InvestigationPayload


class AIKubernetesAgent:
    """Generate a Kubernetes diagnosis from investigation evidence."""

    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        llm_client: OpenRouterClient | None = None,
        root_cause_analyzer: RootCauseAnalyzer | None = None,
        fix_engine: FixRecommendationEngine | None = None,
        confidence_engine: ConfidenceEngine | None = None,
    ) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm_client = llm_client or OpenRouterClient()
        self.root_cause_analyzer = root_cause_analyzer or RootCauseAnalyzer()
        self.fix_engine = fix_engine or FixRecommendationEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()

    def diagnose(self, investigation: InvestigationPayload) -> Diagnosis:
        """Return an LLM-backed diagnosis with a deterministic fallback."""

        messages = self.prompt_builder.build_messages(investigation)
        llm_result = self.llm_client.complete(messages)

        if llm_result.success and llm_result.content:
            parsed = self._parse_llm_diagnosis(llm_result.content)
            if parsed is not None:
                return parsed

        logger.warning("Using fallback diagnosis because LLM reasoning was unavailable")
        fallback = self._build_fallback_diagnosis(investigation)
        if llm_result.error:
            fallback.errors.append(llm_result.error)
        return fallback

    def _parse_llm_diagnosis(self, content: str) -> Diagnosis | None:
        try:
            payload = self._extract_json(content)
            commands = payload.get("kubectl_commands", [])
            if isinstance(commands, str):
                commands = [commands]

            diagnosis = Diagnosis(
                root_cause=payload.get("root_cause", "Unknown root cause"),
                explanation=payload.get("explanation", ""),
                fix=payload.get("fix", ""),
                kubectl_command=commands[0] if commands else "",
                kubectl_commands=commands,
                prevention_recommendation=payload.get("prevention_recommendation", ""),
                confidence=int(payload.get("confidence", 50)),
                confidence_reasoning=payload.get("confidence_reasoning", []),
                source="llm",
            )
            return diagnosis
        except (json.JSONDecodeError, TypeError, ValueError, ValidationError) as exc:
            logger.warning("Could not parse LLM diagnosis: {}", exc.__class__.__name__)
            return None

    def _extract_json(self, content: str) -> dict[str, Any]:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            stripped = stripped.removeprefix("json").strip()

        return json.loads(stripped)

    def _build_fallback_diagnosis(self, investigation: InvestigationPayload) -> Diagnosis:
        root_cause = self.root_cause_analyzer.analyze(investigation)
        fix, commands, prevention = self.fix_engine.recommend(root_cause, investigation)
        confidence, confidence_reasoning = self.confidence_engine.score(
            root_cause,
            investigation,
        )

        return Diagnosis(
            root_cause=root_cause,
            explanation=self._build_explanation(root_cause, investigation),
            fix=fix,
            kubectl_command=commands[0] if commands else "",
            kubectl_commands=commands,
            prevention_recommendation=prevention,
            confidence=confidence,
            confidence_reasoning=confidence_reasoning,
            source="fallback",
        )

    def _build_explanation(
        self,
        root_cause: str,
        investigation: InvestigationPayload,
    ) -> str:
        evidence: list[str] = []

        if investigation.pods.problematic_pods:
            pod = investigation.pods.problematic_pods[0]
            evidence.append(f"pod {pod.namespace}/{pod.name} is in {pod.status}")

        if investigation.logs.logs and investigation.logs.logs[0].findings:
            evidence.append(f"logs show: {investigation.logs.logs[0].findings[0]}")

        if investigation.events.findings:
            event = investigation.events.findings[0]
            evidence.append(f"event {event.reason}: {event.message}")

        if investigation.deployments.unhealthy_deployments:
            deployment = investigation.deployments.unhealthy_deployments[0]
            evidence.append(
                f"deployment {deployment.namespace}/{deployment.name} has "
                f"{deployment.unavailable_replicas} unavailable replicas"
            )

        if investigation.network.issues:
            issue = investigation.network.issues[0]
            evidence.append(f"network issue {issue.type}: {issue.message}")

        if not evidence:
            evidence.append("the collected evidence does not contain a strong failure signal")

        return f"{root_cause} This is based on: {'; '.join(evidence)}."


def reason_about_cluster_state(investigation: InvestigationPayload) -> Diagnosis:
    """Generate a diagnosis for collected Kubernetes evidence."""

    return AIKubernetesAgent().diagnose(investigation)
