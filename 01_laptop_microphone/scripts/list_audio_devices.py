#!/usr/bin/env python3
"""List available audio input devices."""

from __future__ import annotations

from pathlib import Path
import sys

STAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_ROOT / "src"))

from audio_devices import print_input_devices


if __name__ == "__main__":
    print_input_devices()
