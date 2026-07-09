from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

try:
    from ai_analyzer import AIAnalyzerError, analyze_resources
    from azure_scanner import AzureCliError, list_resource_groups, list_resources
except ModuleNotFoundError:
    from .ai_analyzer import AIAnalyzerError, analyze_resources
    from .azure_scanner import AzureCliError, list_resource_groups, list_resources


app = FastAPI(title="AI Cloud Cost Detective API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    resource_group: str = Field(..., min_length=1)


@app.get("/api/resource-groups")
def get_resource_groups() -> dict[str, object]:
    """Return Azure resource groups from the current Azure CLI context."""
    try:
        resource_groups = list_resource_groups()
    except AzureCliError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "resource_groups": resource_groups,
        "count": len(resource_groups),
    }


@app.post("/api/analyze")
def analyze_resource_group(request: AnalyzeRequest) -> dict[str, object]:
    """Scan Azure resources and return AI-powered cost analysis (step ⑤)."""
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
        analysis = analyze_resources(resource_group, resources)
    except AIAnalyzerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "resource_group": resource_group,
        "resources": resources,
        "count": len(resources),
        "analysis": analysis,
    }
