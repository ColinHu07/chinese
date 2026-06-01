#!/usr/bin/env python3
"""List audio input devices for Bluetooth microphone selection."""

from __future__ import annotations

from pathlib import Path
import sys

STAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = STAGE_ROOT.parents[0]
STAGE_ONE_SRC = REPO_ROOT / "01_laptop_microphone" / "src"
sys.path.insert(0, str(STAGE_ONE_SRC))

from audio_devices import print_input_devices


if __name__ == "__main__":
    print_input_devices()
