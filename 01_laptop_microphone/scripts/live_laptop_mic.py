#!/usr/bin/env python3
"""Live Mandarin-to-English captions from the laptop microphone."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

STAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_ROOT / "src"))

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
from logging_utils import JsonlSessionLogger, optional_float
from recorder import LiveAudioRecorder, rms_energy
from translator import WhisperTranslator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--device-index", default="auto", help="Input device index or 'auto'")
    parser.add_argument("--chunk-seconds", type=float, default=DEFAULT_CHUNK_SECONDS)
    parser.add_argument("--overlap-seconds", type=float, default=DEFAULT_OVERLAP_SECONDS)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--rms-threshold", type=float, default=DEFAULT_RMS_THRESHOLD)
    parser.add_argument("--buffer-seconds", type=float, default=DEFAULT_BUFFER_SECONDS)
    parser.add_argument("--log-dir", default=DEFAULT_LOG_DIR)
    parser.add_argument("--list-devices", action="store_true")
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
    translator = WhisperTranslator(
        WhisperConfig(model=args.model, language=args.language, task="translate")
    )
    recorder = LiveAudioRecorder(
        device_index=device_index,
        sample_rate=SAMPLE_RATE,
        buffer_seconds=audio_config.buffer_seconds,
    )
    deduper = CaptionDeduper()
    printer = CaptionPrinter()
    logger = JsonlSessionLogger(args.log_dir)

    print("Loading Whisper model...")
    translator.load()
    print(
        "Listening. Press Ctrl+C to stop. "
        f"model={args.model} chunk={audio_config.chunk_seconds}s overlap={audio_config.overlap_seconds}s"
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

            if energy >= audio_config.rms_threshold:
                caption = translator.translate_audio(audio, sample_rate=SAMPLE_RATE)
                inference_seconds = time.perf_counter() - started
                display = deduper.filter(caption)
                if display:
                    printer.print(display)

            logger.write(
                {
                    "chunk_id": chunk_id,
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "chunk_seconds": audio_config.chunk_seconds,
                    "overlap_seconds": audio_config.overlap_seconds,
                    "model": args.model,
                    "sample_rate": SAMPLE_RATE,
                    "rms": round(energy, 6),
                    "rms_threshold": audio_config.rms_threshold,
                    "skipped_silence": energy < audio_config.rms_threshold,
                    "inference_seconds": optional_float(inference_seconds),
                    "caption": caption,
                }
            )
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        recorder.stop()


if __name__ == "__main__":
    main()
