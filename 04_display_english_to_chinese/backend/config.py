"""Environment-backed settings for the display caption prototype."""

from __future__ import annotations

from dataclasses import dataclass
import os


try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional at import time
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    translator_backend: str = os.getenv("TRANSLATOR_BACKEND", "mock")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    caption_ws_path: str = os.getenv("CAPTION_WS_PATH", "/ws/captions")


settings = Settings()
