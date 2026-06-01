"""JSONL logging helpers for caption sessions."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Optional


class JsonlSessionLogger:
    def __init__(self, log_dir: str | Path, prefix: str = "session") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = self.log_dir / f"{prefix}_{stamp}.jsonl"

    def write(self, event: dict[str, Any]) -> None:
        payload = {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def close(self) -> None:
        return None


def optional_float(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 4)
