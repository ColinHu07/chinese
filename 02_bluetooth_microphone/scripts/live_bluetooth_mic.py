#!/usr/bin/env python3
"""Live Mandarin-to-English captions from a selected Bluetooth microphone."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

STAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = STAGE_ROOT.parents[0]
STAGE_ONE_SRC = REPO_ROOT / "01_laptop_microphone" / "src"
sys.path.insert(0, str(STAGE_ONE_SRC))

from audio_devices import print_input_devices, resolve_input_device
from captions import CaptionDeduper, CaptionPrinter
from config import (
    DEFAULT_BUFFER_SECONDS,
    DEFAULT_CHUNK_SECONDS,
    DEFAULT_LANGUAGE,
    DEFAULT_LOG_DIR,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP_SECONDS,
    DEFAULT_RMS_THRESHOLD,
    SAMPLE_RATE,
    AudioConfig,
    WhisperConfig,
)
from display_bridge import DisplayBridgeError, DisplayCaption, DisplayCaptionClient
from logging_utils import JsonlSessionLogger, optional_float
from recorder import LiveAudioRecorder, rms_energy
from text_translation import BaiduTranslator, TextTranslationError
from translator import WhisperTranslator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--device-index", default="auto", help="Bluetooth input device index or 'auto'")
    parser.add_argument("--chunk-seconds", type=float, default=DEFAULT_CHUNK_SECONDS)
    parser.add_argument("--overlap-seconds", type=float, default=DEFAULT_OVERLAP_SECONDS)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--rms-threshold", type=float, default=DEFAULT_RMS_THRESHOLD)
    parser.add_argument("--buffer-seconds", type=float, default=DEFAULT_BUFFER_SECONDS)
    parser.add_argument("--log-dir", default=DEFAULT_LOG_DIR)
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("whisper", "baidu"),
        default="whisper",
        help="whisper uses Whisper task=translate; baidu transcribes Chinese then calls Baidu zh->en.",
    )
    parser.add_argument("--target-language", default="en", help="Text translation target language for Baidu mode")
    parser.add_argument("--show-source", action="store_true", help="Show Chinese transcript under Baidu output")
    parser.add_argument(
        "--display-url",
        default="",
        help="Optional display backend POST URL, e.g. http://127.0.0.1:8000/caption",
    )
    parser.add_argument(
        "--display-mode",
        choices=("zh_to_en", "en_to_zh"),
        default="zh_to_en",
        help="Caption direction sent to the display backend.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_devices:
        print_input_devices()
        return
    if args.overlap_seconds >= args.chunk_seconds:
        raise SystemExit("--overlap-seconds must be smaller than --chunk-seconds")

    device_index = resolve_input_device(args.device_index)
    audio_config = AudioConfig(
        chunk_seconds=args.chunk_seconds,
        overlap_seconds=args.overlap_seconds,
        buffer_seconds=args.buffer_seconds,
        rms_threshold=args.rms_threshold,
    )
    whisper_task = "transcribe" if args.mode == "baidu" else "translate"
    translator = WhisperTranslator(
        WhisperConfig(model=args.model, language=args.language, task=whisper_task)
    )
    text_translator = None
    if args.mode == "baidu":
        try:
            text_translator = BaiduTranslator.from_env()
        except TextTranslationError as exc:
            raise SystemExit(str(exc)) from exc
    recorder = LiveAudioRecorder(
        device_index=device_index,
        sample_rate=SAMPLE_RATE,
        buffer_seconds=audio_config.buffer_seconds,
    )
    deduper = CaptionDeduper()
    printer = CaptionPrinter()
    logger = JsonlSessionLogger(args.log_dir, prefix="bluetooth_session")
    display_client = DisplayCaptionClient(args.display_url) if args.display_url else None

    print("Loading Whisper model...")
    translator.load()
    print(
        "Listening on Bluetooth/default input. Press Ctrl+C to stop. "
        f"device={args.device_index} model={args.model} mode={args.mode}"
    )

    chunk_id = 0
    recorder.start()
    try:
        while True:
            time.sleep(audio_config.stride_seconds)
            if not recorder.buffer.has_seconds(audio_config.chunk_seconds):
                continue

            chunk_id += 1
            audio = recorder.buffer.snapshot(audio_config.chunk_seconds)
            energy = rms_energy(audio)
            started = time.perf_counter()
            caption = ""
            inference_seconds = None
            source_text = ""
            translation_error = ""
            display_error = ""

            if energy >= audio_config.rms_threshold:
                source_text = translator.translate_audio(audio, sample_rate=SAMPLE_RATE)
                if args.mode == "baidu" and text_translator is not None:
                    try:
                        caption = text_translator.translate(
                            source_text,
                            source_lang=args.language,
                            target_lang=args.target_language,
                        )
                    except TextTranslationError as exc:
                        translation_error = str(exc)
                        print(f"[translation] {translation_error}", file=sys.stderr)
                        caption = ""
                else:
                    caption = source_text
                inference_seconds = time.perf_counter() - started
                display = deduper.filter(caption)
                if display:
                    if args.show_source and source_text and args.mode == "baidu":
                        printer.print(f"{display}\n  zh: {source_text}")
                    else:
                        printer.print(display)
                    if display_client is not None:
                        try:
                            display_client.post(
                                DisplayCaption(
                                    mode=args.display_mode,
                                    source_text=source_text if args.mode == "baidu" else "",
                                    target_text=caption,
                                    latency_ms=int((inference_seconds or 0) * 1000),
                                )
                            )
                        except DisplayBridgeError as exc:
                            display_error = str(exc)
                            print(f"[display] {display_error}", file=sys.stderr)

            logger.write(
                {
                    "chunk_id": chunk_id,
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "stage": "bluetooth_microphone",
                    "device_index": args.device_index,
                    "chunk_seconds": audio_config.chunk_seconds,
                    "overlap_seconds": audio_config.overlap_seconds,
                    "model": args.model,
                    "mode": args.mode,
                    "whisper_task": whisper_task,
                    "sample_rate": SAMPLE_RATE,
                    "rms": round(energy, 6),
                    "rms_threshold": audio_config.rms_threshold,
                    "skipped_silence": energy < audio_config.rms_threshold,
                    "inference_seconds": optional_float(inference_seconds),
                    "source_text": source_text,
                    "caption": caption,
                    "translation_error": translation_error,
                    "display_url": args.display_url,
                    "display_error": display_error,
                }
            )
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        recorder.stop()


if __name__ == "__main__":
    main()
