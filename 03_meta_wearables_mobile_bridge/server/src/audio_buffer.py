"""Helpers for decoding streamed PCM frames."""

from __future__ import annotations

import numpy as np


def decode_pcm_frame(payload: bytes, pcm_format: str) -> np.ndarray:
    """Decode a WebSocket binary frame into mono float32 audio."""

    if not payload:
        return np.zeros(0, dtype=np.float32)

    if pcm_format == "int16":
        audio = np.frombuffer(payload, dtype="<i2").astype(np.float32) / 32768.0
    elif pcm_format == "float32":
        audio = np.frombuffer(payload, dtype="<f4").astype(np.float32)
    else:
        raise ValueError(f"Unsupported PCM format: {pcm_format}")

    return np.ascontiguousarray(audio)
