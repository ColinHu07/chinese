"""Translator interface."""

from __future__ import annotations

from typing import Protocol


class Translator(Protocol):
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
        """Translate text from source_lang to target_lang."""
