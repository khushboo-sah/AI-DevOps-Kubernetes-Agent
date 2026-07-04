"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.clusters import router as clusters_router
from app.api.health import router as health_router
from app.api.investigation import router as investigation_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Configure application startup and shutdown behavior."""

    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("Starting {}", settings.service_name)
    yield
    logger.info("Stopping {}", settings.service_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title="AI Kubernetes Agent API",
        description="Orchestrator API for on-demand Kubernetes troubleshooting.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(clusters_router)
    app.include_router(investigation_router)
    return app


app = create_app()
