"""Caption payload construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_caption_payload(
    source_text: str,
    target_text: str,
    *,
    is_final: bool = True,
    latency_ms: int = 0,
    created_at: str | None = None,
) -> dict[str, Any]:
    return {
        "type": "caption",
        "mode": "en_to_zh",
        "source_text": source_text,
        "target_text": target_text,
        "is_final": is_final,
        "latency_ms": latency_ms,
        "created_at": created_at or utc_now_iso(),
    }


def build_status_payload(status: str) -> dict[str, str]:
    return {
        "type": "status",
        "status": status,
    }
