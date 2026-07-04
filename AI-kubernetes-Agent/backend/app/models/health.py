"""Response models for service health checks."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response returned by GET /health."""

    status: str
    service: str
