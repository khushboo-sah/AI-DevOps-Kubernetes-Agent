"""Azure Managed PostgreSQL connection and queries."""

from __future__ import annotations

import json
import os
from typing import Any

import asyncpg

pool: asyncpg.Pool | None = None


class DatabaseError(Exception):
    """Raised when a database operation cannot be completed."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

CREATE_ANALYSES_TABLE = """
CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_group VARCHAR(255) NOT NULL,
    resources_scanned INTEGER NOT NULL,
    issues_found INTEGER NOT NULL,
    estimated_savings TEXT,
    analysis_result JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""


async def init_db() -> None:
    """Create the connection pool and ensure required tables exist."""
    global pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise DatabaseError(
            "DATABASE_URL is not configured. Add it to your .env file.",
            status_code=503,
        )

    pool = await asyncpg.create_pool(database_url)

    assert pool is not None
    async with pool.acquire() as connection:
        await connection.execute(CREATE_USERS_TABLE)
        await connection.execute(CREATE_ANALYSES_TABLE)


async def close_db() -> None:
    """Close the database connection pool."""
    global pool

    if pool is not None:
        await pool.close()
        pool = None


def _get_pool() -> asyncpg.Pool:
    if pool is None:
        raise DatabaseError(
            "Database is not initialized. Check DATABASE_URL and server startup.",
            status_code=503,
        )
    return pool


async def save_analysis(
    *,
    user_id: int | None,
    resource_group: str,
    resources_scanned: int,
    issues_found: int,
    estimated_savings: str,
    analysis_result: dict[str, Any],
    status: str,
) -> int:
    """Persist a completed analysis and return its database id."""
    db_pool = _get_pool()

    async with db_pool.acquire() as connection:
        row = await connection.fetchrow(
            """
            INSERT INTO analyses (
                user_id,
                resource_group,
                resources_scanned,
                issues_found,
                estimated_savings,
                analysis_result,
                status
            )
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)
            RETURNING id
            """,
            user_id,
            resource_group,
            resources_scanned,
            issues_found,
            estimated_savings,
            json.dumps(analysis_result),
            status,
        )

    return int(row["id"])


async def get_history_for_user(user_id: int) -> list[dict[str, Any]]:
    """Return past analyses for the authenticated user."""
    db_pool = _get_pool()

    async with db_pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT
                id,
                user_id,
                resource_group,
                resources_scanned,
                issues_found,
                estimated_savings,
                analysis_result,
                status,
                created_at
            FROM analyses
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )

    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "resource_group": row["resource_group"],
            "resources_scanned": row["resources_scanned"],
            "issues_found": row["issues_found"],
            "estimated_savings": row["estimated_savings"],
            "analysis_result": json.loads(row["analysis_result"])
            if isinstance(row["analysis_result"], str)
            else row["analysis_result"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat(),
        }
        for row in rows
    ]
