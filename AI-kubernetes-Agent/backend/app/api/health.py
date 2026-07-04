"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health for load balancers and local checks."""

    settings = get_settings()
    return HealthResponse(status="healthy", service=settings.service_name)
