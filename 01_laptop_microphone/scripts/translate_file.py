#!/usr/bin/env python3
"""Translate a Mandarin audio file into English text with local Whisper."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

STAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_ROOT / "src"))

from config import DEFAULT_LANGUAGE, DEFAULT_MODEL, DEFAULT_TASK, WhisperConfig
from text_translation import BaiduTranslator, TextTranslationError
from translator import WhisperTranslator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Path to a Mandarin audio file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Whisper model: tiny, base, small, medium, large")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Input language code, default zh")
    parser.add_argument("--task", default=DEFAULT_TASK, choices=("translate", "transcribe"))
    parser.add_argument(
        "--mode",
        choices=("whisper", "baidu"),
        default="whisper",
        help="whisper uses --task; baidu transcribes Chinese then calls Baidu zh->en.",
    )
    parser.add_argument("--target-language", default="en", help="Text translation target language for Baidu mode")
    parser.add_argument("--show-source", action="store_true", help="Print Chinese transcript before Baidu output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audio_path = Path(args.file)
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")

    task = "transcribe" if args.mode == "baidu" else args.task
    translator = WhisperTranslator(
        WhisperConfig(model=args.model, language=args.language, task=task)
    )
    result = translator.translate_file(audio_path)
    if args.mode == "baidu":
        try:
            text_translator = BaiduTranslator.from_env()
            translated = text_translator.translate(
                result,
                source_lang=args.language,
                target_lang=args.target_language,
            )
        except TextTranslationError as exc:
            raise SystemExit(str(exc)) from exc
        if args.show_source:
            print(f"Chinese transcript: {result}")
        print(translated)
    else:
        print(result)


if __name__ == "__main__":
    main()
