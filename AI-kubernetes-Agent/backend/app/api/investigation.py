"""Kubernetes investigation endpoint."""

from fastapi import APIRouter

from app.models.investigation import InvestigationResponse
from app.services.investigation_service import InvestigationService

router = APIRouter(tags=["investigation"])


@router.post("/investigate", response_model=InvestigationResponse)
def investigate_cluster() -> InvestigationResponse:
    """Collect Kubernetes evidence and return an AI-assisted diagnosis."""

    service = InvestigationService()
    investigation = service.run_investigation()
    diagnosis = service.diagnose_investigation(investigation)
    return InvestigationResponse(
        status="success",
        investigation=investigation,
        diagnosis=diagnosis,
    )
