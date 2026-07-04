"""OpenRouter LLM client."""

from dataclasses import dataclass
from time import sleep

import httpx
from loguru import logger

from app.core.config import get_settings

OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"


@dataclass(frozen=True)
class LLMResult:
    """Result from an LLM completion call."""

    success: bool
    content: str | None = None
    error: str | None = None


class OpenRouterClient:
    """Simple OpenRouter chat completion client."""

    def __init__(self, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def complete(self, messages: list[dict[str, str]]) -> LLMResult:
        """Send messages to OpenRouter and return the assistant content."""

        settings = get_settings()
        if not settings.openrouter_api_key:
            return LLMResult(
                success=False,
                error="OPENROUTER_API_KEY is not configured",
            )

        model = settings.openrouter_model or DEFAULT_OPENROUTER_MODEL
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        for attempt in range(1, self.max_retries + 2):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        OPENROUTER_CHAT_COMPLETIONS_URL,
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return LLMResult(success=True, content=content)
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                error = f"OpenRouter request failed: {exc.__class__.__name__}"
                logger.warning("{} on attempt {}", error, attempt)
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                error = f"OpenRouter returned HTTP {status_code}"
                logger.warning("{} on attempt {}", error, attempt)
            except (KeyError, ValueError) as exc:
                error = f"OpenRouter response could not be parsed: {exc.__class__.__name__}"
                logger.warning("{} on attempt {}", error, attempt)

            if attempt <= self.max_retries:
                sleep(0.5 * attempt)

        return LLMResult(success=False, error=error)
