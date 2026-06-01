"""Local WebSocket server for mobile audio streaming."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

from client_session import ClientSession
from stage_one_path import add_stage_one_src

add_stage_one_src()

from config import (
    DEFAULT_CHUNK_SECONDS,
    DEFAULT_LANGUAGE,
    DEFAULT_LOG_DIR,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP_SECONDS,
    DEFAULT_RMS_THRESHOLD,
    SAMPLE_RATE,
    WhisperConfig,
)
from logging_utils import JsonlSessionLogger
from translator import WhisperTranslator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--sample-rate", type=int, default=SAMPLE_RATE)
    parser.add_argument("--chunk-seconds", type=float, default=DEFAULT_CHUNK_SECONDS)
    parser.add_argument("--overlap-seconds", type=float, default=DEFAULT_OVERLAP_SECONDS)
    parser.add_argument("--rms-threshold", type=float, default=DEFAULT_RMS_THRESHOLD)
    parser.add_argument("--pcm-format", choices=("int16", "float32"), default="int16")
    parser.add_argument("--log-dir", default=str(Path(DEFAULT_LOG_DIR)))
    return parser.parse_args()


async def serve(args: argparse.Namespace) -> None:
    try:
        import websockets
    except ImportError as exc:  # pragma: no cover - install dependent
        raise RuntimeError("Install server requirements with `pip install -r requirements.txt`.") from exc

    translator = WhisperTranslator(
        WhisperConfig(model=args.model, language=args.language, task="translate")
    )
    print("Loading Whisper model...")
    translator.load()
    logger = JsonlSessionLogger(args.log_dir, prefix="ws_session")
    inference_lock = asyncio.Lock()

    async def handler(websocket: Any, path: str | None = None) -> None:
        session = ClientSession(
            websocket=websocket,
            translator=translator,
            inference_lock=inference_lock,
            logger=logger,
            sample_rate=args.sample_rate,
            chunk_seconds=args.chunk_seconds,
            overlap_seconds=args.overlap_seconds,
            rms_threshold=args.rms_threshold,
            pcm_format=args.pcm_format,
        )
        await session.run()

    print(f"Serving ws://{args.host}:{args.port} with model={args.model}")
    async with websockets.serve(handler, args.host, args.port, max_size=None):
        await asyncio.Future()


def main() -> None:
    args = parse_args()
    if args.overlap_seconds >= args.chunk_seconds:
        raise SystemExit("--overlap-seconds must be smaller than --chunk-seconds")
    asyncio.run(serve(args))


if __name__ == "__main__":
    main()
