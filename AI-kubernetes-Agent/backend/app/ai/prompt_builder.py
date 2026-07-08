"""Build deterministic prompts for Kubernetes troubleshooting."""

import json

from app.models.investigation import InvestigationPayload

SYSTEM_PROMPT = """You are a Senior Kubernetes SRE.
You diagnose production Kubernetes incidents by correlating pods, logs, events,
deployment health, and networking evidence. Be practical, specific, and
beginner friendly. Do not invent evidence that is not present.

Return only valid JSON with these keys:
root_cause, explanation, fix, kubectl_commands, prevention_recommendation,
confidence, confidence_reasoning.

Rules:
- root_cause: one concise sentence naming the most likely cause. If evidence shows a
  Kubernetes pod status (e.g. CrashLoopBackOff, ImagePullBackOff, OOMKilled), include
  that status in the root_cause sentence.
- explanation: explain how the evidence connects to that cause.
- fix: one practical Kubernetes-specific fix.
- kubectl_commands: an array of safe commands the user can run next.
- prevention_recommendation: how to prevent recurrence.
- confidence: integer from 0 to 100.
- confidence_reasoning: array of short evidence-based reasons.
"""


class PromptBuilder:
    """Create LLM prompts from collected Kubernetes evidence."""

    def build_messages(self, investigation: InvestigationPayload) -> list[dict[str, str]]:
        """Return OpenRouter-compatible chat messages."""

        evidence = investigation.model_dump(mode="json")

        user_prompt = f"""Analyze this Kubernetes investigation evidence.

Focus on:
1. Pod Status
2. Logs
3. Events
4. Deployment Health
5. Networking Findings

Kubernetes evidence JSON:
{json.dumps(evidence, indent=2)}

Return the JSON diagnosis now."""

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
