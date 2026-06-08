"""FastAPI backend for display-only English-to-Chinese caption testing."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from .captions import build_caption_payload
from .config import settings
from .translation import ArgosTranslator, MockTranslator, Translator
from .websocket_manager import WebSocketManager


class CaptionRequest(BaseModel):
    source_text: str = Field(default="", description="Original English text")
    target_text: str = Field(..., min_length=1, description="Simplified Chinese caption")
    is_final: bool = True
    latency_ms: int = Field(default=0, ge=0)


class HealthResponse(BaseModel):
    ok: Literal[True]
    translator_backend: str
    caption_ws_path: str
    connected_clients: int


class TestCaptionResponse(BaseModel):
    ok: Literal[True]
    broadcasted: bool
    connected_clients: int
    payload: dict


def create_translator(name: str) -> Translator:
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockTranslator()
    if normalized == "argos":
        return ArgosTranslator()
    raise RuntimeError(f"Unknown TRANSLATOR_BACKEND={name!r}. Use 'mock' or 'argos'.")


app = FastAPI(title="English-to-Chinese Display Caption Prototype")
manager = WebSocketManager()
translator = create_translator(settings.translator_backend)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        ok=True,
        translator_backend=settings.translator_backend,
        caption_ws_path=settings.caption_ws_path,
        connected_clients=manager.client_count,
    )


@app.post("/test-caption", response_model=TestCaptionResponse)
async def test_caption(request: CaptionRequest) -> TestCaptionResponse:
    payload = build_caption_payload(
        source_text=request.source_text,
        target_text=request.target_text,
        is_final=request.is_final,
        latency_ms=request.latency_ms,
    )
    connected_clients = await manager.broadcast(payload)
    return TestCaptionResponse(
        ok=True,
        broadcasted=True,
        connected_clients=connected_clients,
        payload=payload,
    )


@app.websocket(settings.caption_ws_path)
async def captions_socket(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
