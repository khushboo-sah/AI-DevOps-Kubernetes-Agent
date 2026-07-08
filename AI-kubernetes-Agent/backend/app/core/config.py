"""Application configuration loaded from environment variables."""

from functools import lru_cache
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_ROOT / ".env")


class Settings(BaseModel):
    """Runtime settings for the FastAPI service."""

    service_name: str = "ai-kubernetes-agent"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    insforge_api_base_url: str | None = None
    openrouter_api_key: str | None = None
    openrouter_model: str | None = None
    kubeconfig_path: str | None = None


def _split_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default

    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings from the current process environment."""

    api_key = getenv("OPENROUTER_API_KEY")
    if api_key is not None and not api_key.strip():
        api_key = None

    return Settings(
        log_level=getenv("LOG_LEVEL", "INFO"),
        cors_origins=_split_csv(getenv("CORS_ORIGINS"), ["http://localhost:3000"]),
        insforge_api_base_url=getenv("INSFORGE_API_BASE_URL"),
        openrouter_api_key=api_key,
        openrouter_model=getenv("OPENROUTER_MODEL"),
        kubeconfig_path=getenv("KUBECONFIG_PATH") or None,
    )
