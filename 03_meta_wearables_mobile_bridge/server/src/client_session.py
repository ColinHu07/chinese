"""Per-client WebSocket session processing."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import time
from typing import Any
from uuid import uuid4

import numpy as np

from audio_buffer import decode_pcm_frame
from stage_one_path import add_stage_one_src

add_stage_one_src()

from captions import CaptionDeduper
from logging_utils import JsonlSessionLogger, optional_float
from recorder import RollingAudioBuffer, rms_energy
from translator import WhisperTranslator


class ClientSession:
    def __init__(
        self,
        websocket: Any,
        translator: WhisperTranslator,
        inference_lock: asyncio.Lock,
        logger: JsonlSessionLogger,
        sample_rate: int,
        chunk_seconds: float,
        overlap_seconds: float,
        rms_threshold: float,
        pcm_format: str,
    ) -> None:
        self.websocket = websocket
        self.translator = translator
        self.inference_lock = inference_lock
        self.logger = logger
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.stride_seconds = max(0.25, chunk_seconds - overlap_seconds)
        self.overlap_seconds = overlap_seconds
        self.rms_threshold = rms_threshold
        self.pcm_format = pcm_format
        self.client_id = str(uuid4())
        self.buffer = RollingAudioBuffer(sample_rate=sample_rate, max_seconds=max(30.0, chunk_seconds * 4))
        self.deduper = CaptionDeduper()
        self.chunk_id = 0
        self._closed = asyncio.Event()

    async def run(self) -> None:
        await self._send_json(
            {
                "type": "ready",
                "client_id": self.client_id,
                "sample_rate": self.sample_rate,
                "pcm_format": self.pcm_format,
            }
        )
        consumer = asyncio.create_task(self._consume_audio())
        processor = asyncio.create_task(self._process_chunks())
        done, pending = await asyncio.wait(
            {consumer, processor},
            return_when=asyncio.FIRST_COMPLETED,
        )
        self._closed.set()
        for task in pending:
            task.cancel()
        for task in done:
            task.result()

    async def _consume_audio(self) -> None:
        async for message in self.websocket:
            if isinstance(message, bytes):
                self.buffer.append(decode_pcm_frame(message, self.pcm_format))
            else:
                await self._handle_text_message(str(message))
        self._closed.set()

    async def _handle_text_message(self, message: str) -> None:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            await self._send_json({"type": "error", "message": "Text messages must be JSON"})
            return

        if payload.get("type") == "ping":
            await self._send_json({"type": "pong", "client_id": self.client_id})

    async def _process_chunks(self) -> None:
        while not self._closed.is_set():
            await asyncio.sleep(self.stride_seconds)
            if not self.buffer.has_seconds(self.chunk_seconds):
                continue

            self.chunk_id += 1
            audio = self.buffer.snapshot(self.chunk_seconds)
            energy = rms_energy(audio)
            caption = ""
            display_caption = None
            inference_seconds = None
            started = time.perf_counter()

            if energy >= self.rms_threshold:
                async with self.inference_lock:
                    caption = await asyncio.to_thread(
                        self.translator.translate_audio,
                        np.copy(audio),
                        self.sample_rate,
                    )
                inference_seconds = time.perf_counter() - started
                display_caption = self.deduper.filter(caption)
                if display_caption:
                    await self._send_json(
                        {
                            "type": "caption",
                            "client_id": self.client_id,
                            "chunk_id": self.chunk_id,
                            "text": display_caption,
                            "raw_text": caption,
                            "inference_seconds": optional_float(inference_seconds),
                        }
                    )

            self.logger.write(
                {
                    "stage": "meta_wearables_mobile_bridge",
                    "client_id": self.client_id,
                    "chunk_id": self.chunk_id,
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "chunk_seconds": self.chunk_seconds,
                    "overlap_seconds": self.overlap_seconds,
                    "sample_rate": self.sample_rate,
                    "pcm_format": self.pcm_format,
                    "rms": round(energy, 6),
                    "rms_threshold": self.rms_threshold,
                    "skipped_silence": energy < self.rms_threshold,
                    "inference_seconds": optional_float(inference_seconds),
                    "caption": caption,
                    "display_caption": display_caption,
                }
            )

    async def _send_json(self, payload: dict[str, Any]) -> None:
        await self.websocket.send(json.dumps(payload, ensure_ascii=False))
