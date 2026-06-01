#!/usr/bin/env python3
"""Translate a Mandarin audio file into English text with local Whisper."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

STAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_ROOT / "src"))

from config import DEFAULT_LANGUAGE, DEFAULT_MODEL, DEFAULT_TASK, WhisperConfig
from translator import WhisperTranslator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Path to a Mandarin audio file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Whisper model: tiny, base, small, medium, large")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Input language code, default zh")
    parser.add_argument("--task", default=DEFAULT_TASK, choices=("translate", "transcribe"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audio_path = Path(args.file)
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")

    translator = WhisperTranslator(
        WhisperConfig(model=args.model, language=args.language, task=args.task)
    )
    print(translator.translate_file(audio_path))


if __name__ == "__main__":
    main()
