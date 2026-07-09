"""WebSocket progress broadcasting for analysis runs."""

from __future__ import annotations

from fastapi import WebSocket


class ProgressManager:
    """Track WebSocket connections per analysis id."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, analysis_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(analysis_id, []).append(websocket)

    def disconnect(self, analysis_id: str, websocket: WebSocket) -> None:
        connections = self._connections.get(analysis_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._connections.pop(analysis_id, None)

    async def send(self, analysis_id: str, message: str) -> None:
        for websocket in list(self._connections.get(analysis_id, [])):
            try:
                await websocket.send_text(message)
            except Exception:
                self.disconnect(analysis_id, websocket)
