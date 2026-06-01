"""Default configuration for the local translator prototype."""

from __future__ import annotations

from dataclasses import dataclass


SAMPLE_RATE = 16_000
CHANNELS = 1
DTYPE = "float32"
DEFAULT_MODEL = "base"
DEFAULT_LANGUAGE = "zh"
DEFAULT_TASK = "translate"
DEFAULT_CHUNK_SECONDS = 5.0
DEFAULT_OVERLAP_SECONDS = 1.0
DEFAULT_BUFFER_SECONDS = 30.0
DEFAULT_RMS_THRESHOLD = 0.005
DEFAULT_LOG_DIR = "logs"
SUPPORTED_MODELS = ("tiny", "base", "small", "medium", "large")


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int = SAMPLE_RATE
    channels: int = CHANNELS
    dtype: str = DTYPE
    chunk_seconds: float = DEFAULT_CHUNK_SECONDS
    overlap_seconds: float = DEFAULT_OVERLAP_SECONDS
    buffer_seconds: float = DEFAULT_BUFFER_SECONDS
    rms_threshold: float = DEFAULT_RMS_THRESHOLD

    @property
    def stride_seconds(self) -> float:
        return max(0.25, self.chunk_seconds - self.overlap_seconds)


@dataclass(frozen=True)
class WhisperConfig:
    model: str = DEFAULT_MODEL
    language: str = DEFAULT_LANGUAGE
    task: str = DEFAULT_TASK
    temperature: float = 0.0
    condition_on_previous_text: bool = False
    no_speech_threshold: float = 0.6
