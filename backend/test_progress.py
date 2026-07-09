"""Tests for WebSocket progress manager."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

from progress import ProgressManager


class TestProgressManager(unittest.IsolatedAsyncioTestCase):
    async def test_send_delivers_message_to_connected_client(self) -> None:
        manager = ProgressManager()
        websocket = AsyncMock()
        websocket.accept = AsyncMock()

        await manager.connect("analysis-1", websocket)
        await manager.send("analysis-1", "Scanning resources in rg-demo...")

        websocket.accept.assert_awaited_once()
        websocket.send_text.assert_awaited_once_with(
            "Scanning resources in rg-demo..."
        )

    async def test_disconnect_removes_client(self) -> None:
        manager = ProgressManager()
        websocket = AsyncMock()
        websocket.accept = AsyncMock()

        await manager.connect("analysis-1", websocket)
        manager.disconnect("analysis-1", websocket)
        await manager.send("analysis-1", "Analysis complete")

        websocket.send_text.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
