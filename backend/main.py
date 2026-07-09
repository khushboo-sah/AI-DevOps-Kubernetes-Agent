from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

try:
    from ai_analyzer import AIAnalyzerError, analyze_resources
    from auth import AuthError, create_access_token, get_current_user_id, hash_password, verify_password
    from azure_scanner import AzureCliError, list_resource_groups, list_resources
    from db import (
        DatabaseError,
        close_db,
        create_user,
        get_history_for_user,
        get_user_by_email,
        init_db,
        save_analysis,
    )
    from progress import ProgressManager
except ModuleNotFoundError:
    from .ai_analyzer import AIAnalyzerError, analyze_resources
    from .auth import AuthError, create_access_token, get_current_user_id, hash_password, verify_password
    from .azure_scanner import AzureCliError, list_resource_groups, list_resources
    from .db import (
        DatabaseError,
        close_db,
        create_user,
        get_history_for_user,
        get_user_by_email,
        init_db,
        save_analysis,
    )
    from .progress import ProgressManager


progress_manager = ProgressManager()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await init_db()
    except DatabaseError:
        pass
    yield
    await close_db()


app = FastAPI(title="AI Cloud Cost Detective API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class AnalyzeRequest(BaseModel):
    resource_group: str = Field(..., min_length=1)
    analysis_id: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest) -> AuthResponse:
    """Register a new user and return a JWT."""
    try:
        user = await create_user(request.email, hash_password(request.password))
        token = create_access_token(user["id"], user["email"])
    except DatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AuthResponse(
        access_token=token,
        user_id=user["id"],
        email=user["email"],
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """Validate credentials and return a JWT."""
    try:
        user = await get_user_by_email(request.email)
    except DatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    try:
        token = create_access_token(user["id"], user["email"])
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AuthResponse(
        access_token=token,
        user_id=user["id"],
        email=user["email"],
    )


@app.get("/api/resource-groups")
def get_resource_groups(
    _user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict[str, object]:
    """Return Azure resource groups from the current Azure CLI context."""
    try:
        resource_groups = list_resource_groups()
    except AzureCliError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "resource_groups": resource_groups,
        "count": len(resource_groups),
    }


@app.websocket("/ws/progress/{analysis_id}")
async def analysis_progress(websocket: WebSocket, analysis_id: str) -> None:
    """Stream live progress updates for an analysis run."""
    await progress_manager.connect(analysis_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        progress_manager.disconnect(analysis_id, websocket)


@app.get("/api/history")
async def get_analysis_history(
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict[str, object]:
    """Return past analyses for the authenticated user."""
    try:
        history = await get_history_for_user(user_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "analyses": history,
        "count": len(history),
    }


@app.post("/api/analyze")
async def analyze_resource_group(
    request: AnalyzeRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict[str, object]:
    """Scan Azure resources, analyze costs, store results, and stream progress."""
    resource_group = request.resource_group.strip()
    analysis_id = request.analysis_id.strip()

    if not resource_group:
        raise HTTPException(
            status_code=422,
            detail="resource_group cannot be empty.",
        )
    if not analysis_id:
        raise HTTPException(
            status_code=422,
            detail="analysis_id cannot be empty.",
        )

    await progress_manager.send(analysis_id, "Fetching resource groups...")

    try:
        await progress_manager.send(
            analysis_id, f"Scanning resources in {resource_group}..."
        )
        resources = await asyncio.to_thread(list_resources, resource_group)
    except AzureCliError as exc:
        await progress_manager.send(analysis_id, f"Error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    try:
        await progress_manager.send(analysis_id, "Analyzing costs with AI...")
        analysis = await asyncio.to_thread(analyze_resources, resource_group, resources)
    except AIAnalyzerError as exc:
        await progress_manager.send(analysis_id, f"Error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    issues_found = len(analysis.get("issues", []))
    estimated_savings = f"${analysis.get('estimated_total_savings_usd', 0)}/month"

    try:
        await progress_manager.send(analysis_id, "Storing results...")
        stored_id = await save_analysis(
            user_id=user_id,
            resource_group=resource_group,
            resources_scanned=len(resources),
            issues_found=issues_found,
            estimated_savings=estimated_savings,
            analysis_result=analysis,
            status="completed",
        )
    except DatabaseError as exc:
        await progress_manager.send(analysis_id, f"Error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    await progress_manager.send(analysis_id, "Analysis complete")

    return {
        "id": stored_id,
        "resource_group": resource_group,
        "resources": resources,
        "count": len(resources),
        "analysis": analysis,
    }
