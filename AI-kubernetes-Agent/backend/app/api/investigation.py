"""Kubernetes investigation endpoint."""

from fastapi import APIRouter

from app.models.investigation import InvestigationResponse
from app.services.investigation_service import start_investigation

router = APIRouter(tags=["investigation"])


@router.post("/investigate", response_model=InvestigationResponse)
def investigate_cluster() -> InvestigationResponse:
    """Collect Kubernetes troubleshooting evidence."""

    investigation = start_investigation()
    return InvestigationResponse(status="success", investigation=investigation)
