"""Import path helper for reusing Stage 1 translator code."""

from __future__ import annotations

from pathlib import Path
import sys


def add_stage_one_src() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    stage_one_src = repo_root / "01_laptop_microphone" / "src"
    if str(stage_one_src) not in sys.path:
        sys.path.insert(0, str(stage_one_src))
    return stage_one_src
