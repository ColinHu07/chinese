#!/usr/bin/env python3
"""Run the local WebSocket translator server."""

from __future__ import annotations

from pathlib import Path
import sys

SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_ROOT / "src"))

from ws_translator_server import main


if __name__ == "__main__":
    main()
