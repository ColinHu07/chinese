"""Whisper loading and Mandarin-to-English translation wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np

from config import SAMPLE_RATE, WhisperConfig
from recorder import ensure_mono_float32, resample_audio


class WhisperTranslator:
    """Lazy-loading local Whisper translator."""

    def __init__(self, config: WhisperConfig) -> None:
        self.config = config
        self._model: Optional[Any] = None
        self._torch: Optional[Any] = None

    def load(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            import whisper
        except ImportError as exc:  # pragma: no cover - install dependent
            raise RuntimeError(
                "Whisper dependencies are missing. Run `pip install -r requirements.txt` "
                "inside this stage's virtual environment."
            ) from exc

        self._torch = torch
        self._model = whisper.load_model(self.config.model)

    @property
    def model(self) -> Any:
        self.load()
        return self._model

    def _fp16_enabled(self) -> bool:
        if self._torch is None:
            self.load()
        return bool(self._torch and self._torch.cuda.is_available())

    def translate_file(self, path: str | Path) -> str:
        result = self.model.transcribe(
            str(path),
            language=self.config.language,
            task=self.config.task,
            fp16=self._fp16_enabled(),
            temperature=self.config.temperature,
            condition_on_previous_text=self.config.condition_on_previous_text,
            no_speech_threshold=self.config.no_speech_threshold,
        )
        return str(result.get("text", "")).strip()

    def translate_audio(self, audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> str:
        chunk = ensure_mono_float32(audio)
        if sample_rate != SAMPLE_RATE:
            chunk = resample_audio(chunk, sample_rate, SAMPLE_RATE)
        result = self.model.transcribe(
            chunk,
            language=self.config.language,
            task=self.config.task,
            fp16=self._fp16_enabled(),
            temperature=self.config.temperature,
            condition_on_previous_text=self.config.condition_on_previous_text,
            no_speech_threshold=self.config.no_speech_threshold,
        )
        return str(result.get("text", "")).strip()
