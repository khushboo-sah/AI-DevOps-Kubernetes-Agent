"""Minimal InsForge authentication helpers for API routes."""

from pydantic import BaseModel

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from app.core.config import get_settings

security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Authenticated user returned by InsForge."""

    id: str
    email: str | None = None
    role: str | None = None


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    """Validate the bearer token with InsForge and return the current user."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    settings = get_settings()
    if not settings.insforge_api_base_url:
        logger.error("INSFORGE_API_BASE_URL is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service is not configured",
        )

    try:
        response = httpx.get(
            f"{settings.insforge_api_base_url.rstrip('/')}/api/auth/sessions/current",
            headers={"Authorization": f"Bearer {credentials.credentials}"},
            timeout=10,
        )
    except httpx.RequestError as exc:
        logger.warning("InsForge auth validation failed: {}", exc.__class__.__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        ) from exc

    if response.status_code != status.HTTP_200_OK:
        logger.warning("InsForge rejected bearer token with status {}", response.status_code)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = response.json().get("user")
    if not user or not user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session user",
        )

    return AuthenticatedUser(
        id=user["id"],
        email=user.get("email"),
        role=user.get("role"),
    )
