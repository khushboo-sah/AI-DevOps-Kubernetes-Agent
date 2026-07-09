from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from azure_scanner import AzureCliError, list_resource_groups, list_resources


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
    """Fetch Azure resources for the selected group and return key metadata."""
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

    return {
        "resource_group": resource_group,
        "resources": resources,
        "count": len(resources),
    }
