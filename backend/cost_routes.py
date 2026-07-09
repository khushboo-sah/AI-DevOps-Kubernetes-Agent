"""Cost analysis routes (Request Flow step ⑤)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

try:
    from azure_scanner import AzureCliError, list_resources
    from cost_detector import CostDetectorError, detect_cost_issues
except ModuleNotFoundError:
    from .azure_scanner import AzureCliError, list_resources
    from .cost_detector import CostDetectorError, detect_cost_issues

router = APIRouter()


class CostAnalyzeRequest(BaseModel):
    resource_group: str = Field(..., min_length=1)


@router.post("/api/analyze/cost")
def analyze_resource_cost(request: CostAnalyzeRequest) -> dict[str, object]:
    """Scan Azure resources and return AI-powered cost analysis."""
    resource_group = request.resource_group.strip()
    if not resource_group:
        raise HTTPException(
            status_code=422,
            detail="resource_group cannot be empty.",
        )

    try:
        resources = list_resources(resource_group)
    except AzureCliError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    try:
        analysis = detect_cost_issues(resource_group, resources)
    except CostDetectorError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "resource_group": resource_group,
        "resources": resources,
        "count": len(resources),
        "analysis": analysis,
    }
