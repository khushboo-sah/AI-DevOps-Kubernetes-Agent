"""Logging configuration for the backend service."""

import sys

from loguru import logger


def configure_logging(log_level: str) -> None:
    """Configure Loguru with a simple structured-friendly output."""

    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
