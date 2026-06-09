"""Optional bridge for posting live captions to the display backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class DisplayBridgeError(RuntimeError):
    """Raised when the display bridge cannot send a caption."""


@dataclass(frozen=True)
class DisplayCaption:
    mode: str
    source_text: str
    target_text: str
    is_final: bool = True
    latency_ms: int = 0


class DisplayCaptionClient:
    def __init__(self, url: str, timeout_seconds: float = 2.5, session: Optional[Any] = None) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.session = session

    def post(self, caption: DisplayCaption) -> None:
        payload = {
            "mode": caption.mode,
            "source_text": caption.source_text,
            "target_text": caption.target_text,
            "is_final": caption.is_final,
            "latency_ms": caption.latency_ms,
        }
        session = self.session or self._requests()
        try:
            response = session.post(self.url, json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
        except Exception as exc:
            raise DisplayBridgeError(f"Display caption POST failed: {exc}") from exc

    @staticmethod
    def _requests() -> Any:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover - install dependent
            raise DisplayBridgeError(
                "Display bridge requires requests. Run `pip install -r requirements.txt`."
            ) from exc
        return requests
