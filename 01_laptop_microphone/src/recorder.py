"""Microphone capture, rolling buffers, and audio chunk utilities."""

from __future__ import annotations

import sys
import threading
from fractions import Fraction
from typing import Optional

import numpy as np

from config import SAMPLE_RATE


def samples_for_seconds(seconds: float, sample_rate: int = SAMPLE_RATE) -> int:
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    return int(round(seconds * sample_rate))


def ensure_mono_float32(audio: np.ndarray) -> np.ndarray:
    """Return 1D mono float32 audio."""

    array = np.asarray(audio)
    if array.ndim == 2:
        array = array.mean(axis=1)
    if array.ndim != 1:
        raise ValueError(f"audio must be 1D mono or 2D channel data, got shape {array.shape}")
    return np.ascontiguousarray(array.astype(np.float32, copy=False))


def rms_energy(audio: np.ndarray) -> float:
    array = ensure_mono_float32(audio)
    if array.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(array, dtype=np.float64))))


def resample_audio(audio: np.ndarray, source_rate: int, target_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Resample mono float32 audio with scipy when available, falling back to interpolation."""

    array = ensure_mono_float32(audio)
    if source_rate == target_rate or array.size == 0:
        return array

    try:
        from scipy.signal import resample_poly

        ratio = Fraction(target_rate, source_rate).limit_denominator(1000)
        resampled = resample_poly(array, ratio.numerator, ratio.denominator)
        return ensure_mono_float32(resampled)
    except Exception:
        duration = array.size / float(source_rate)
        target_size = max(1, int(round(duration * target_rate)))
        old_positions = np.linspace(0.0, duration, num=array.size, endpoint=False)
        new_positions = np.linspace(0.0, duration, num=target_size, endpoint=False)
        return ensure_mono_float32(np.interp(new_positions, old_positions, array))


class RollingAudioBuffer:
    """Thread-safe fixed-duration rolling audio buffer."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, max_seconds: float = 30.0) -> None:
        self.sample_rate = sample_rate
        self.max_samples = samples_for_seconds(max_seconds, sample_rate)
        self._audio = np.zeros(0, dtype=np.float32)
        self._lock = threading.Lock()

    @property
    def duration_seconds(self) -> float:
        with self._lock:
            return self._audio.size / float(self.sample_rate)

    def append(self, audio: np.ndarray) -> None:
        chunk = ensure_mono_float32(audio)
        if chunk.size == 0:
            return
        with self._lock:
            merged = np.concatenate((self._audio, chunk))
            if merged.size > self.max_samples:
                merged = merged[-self.max_samples :]
            self._audio = merged

    def snapshot(self, seconds: Optional[float] = None) -> np.ndarray:
        with self._lock:
            if seconds is None:
                return self._audio.copy()
            count = min(samples_for_seconds(seconds, self.sample_rate), self._audio.size)
            return self._audio[-count:].copy()

    def has_seconds(self, seconds: float) -> bool:
        with self._lock:
            return self._audio.size >= samples_for_seconds(seconds, self.sample_rate)


class LiveAudioRecorder:
    """sounddevice InputStream wrapper that keeps a rolling 16 kHz mono buffer."""

    def __init__(
        self,
        device_index: Optional[int],
        sample_rate: int = SAMPLE_RATE,
        channels: int = 1,
        buffer_seconds: float = 30.0,
        dtype: str = "float32",
    ) -> None:
        self.device_index = device_index
        self.target_sample_rate = sample_rate
        self.channels = channels
        self.buffer = RollingAudioBuffer(sample_rate=sample_rate, max_seconds=buffer_seconds)
        self.dtype = dtype
        self.actual_sample_rate = sample_rate
        self._stream = None

    def _sounddevice(self):
        try:
            import sounddevice as sd
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "sounddevice is not installed. Run `pip install -r requirements.txt` "
                "and make sure PortAudio is installed."
            ) from exc
        return sd

    def _callback(self, indata, frames, time_info, status) -> None:  # pragma: no cover - live audio
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        audio = ensure_mono_float32(np.asarray(indata))
        if self.actual_sample_rate != self.target_sample_rate:
            audio = resample_audio(audio, self.actual_sample_rate, self.target_sample_rate)
        self.buffer.append(audio)

    def start(self) -> "LiveAudioRecorder":  # pragma: no cover - live audio
        sd = self._sounddevice()
        try:
            self.actual_sample_rate = self.target_sample_rate
            self._stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.target_sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._callback,
            )
            self._stream.start()
            return self
        except Exception:
            if self._stream is not None:
                self._stream.close()
            device_info = sd.query_devices(self.device_index, "input")
            fallback_rate = int(float(device_info["default_samplerate"]))
            self.actual_sample_rate = fallback_rate
            self._stream = sd.InputStream(
                device=self.device_index,
                samplerate=fallback_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._callback,
            )
            self._stream.start()
            return self

    def stop(self) -> None:  # pragma: no cover - live audio
        if self._stream is None:
            return
        self._stream.stop()
        self._stream.close()
        self._stream = None
