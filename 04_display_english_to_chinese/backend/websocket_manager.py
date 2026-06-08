"""WebSocket connection manager for caption broadcasts."""

from __future__ import annotations

from typing import Any

from fastapi import WebSocket

from .captions import build_status_payload


class WebSocketManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    @property
    def client_count(self) -> int:
        return len(self._clients)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)
        await websocket.send_json(build_status_payload("connected"))

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> int:
        sent = 0
        stale: list[WebSocket] = []
        for websocket in list(self._clients):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
            else:
                sent += 1
        for websocket in stale:
            self.disconnect(websocket)
        return sent
