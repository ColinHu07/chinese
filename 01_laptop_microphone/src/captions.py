"""Terminal caption rendering and overlap de-duplication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
import re
from typing import Optional


def normalize_caption(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return re.sub(r"[^a-z0-9 ]+", "", lowered).strip()


def _similarity(a: str, b: str) -> float:
    try:
        from rapidfuzz import fuzz

        return float(fuzz.ratio(a, b))
    except Exception:
        return SequenceMatcher(None, a, b).ratio() * 100.0


def _word_overlap_suffix(previous: str, current: str) -> str:
    previous_words = previous.split()
    current_words = current.split()
    max_overlap = min(len(previous_words), len(current_words))
    for size in range(max_overlap, 1, -1):
        if previous_words[-size:] == current_words[:size]:
            return " ".join(current_words[size:])
    return current


@dataclass
class CaptionDeduper:
    similarity_threshold: float = 92.0
    last_caption: str = ""

    def filter(self, caption: str) -> Optional[str]:
        candidate = caption.strip()
        if not candidate:
            return None

        previous_norm = normalize_caption(self.last_caption)
        candidate_norm = normalize_caption(candidate)
        if not previous_norm:
            self.last_caption = candidate
            return candidate
        if not candidate_norm:
            return None
        if candidate_norm == previous_norm:
            return None
        if candidate_norm in previous_norm:
            return None

        if candidate_norm.startswith(previous_norm):
            suffix = candidate[len(self.last_caption) :].strip(" ,.;:-")
            self.last_caption = candidate
            return suffix or None

        if _similarity(previous_norm, candidate_norm) >= self.similarity_threshold:
            return None

        suffix = _word_overlap_suffix(previous_norm, candidate_norm)
        if suffix != candidate_norm and suffix:
            original_words = candidate.split()
            suffix_word_count = len(suffix.split())
            self.last_caption = candidate
            return " ".join(original_words[-suffix_word_count:])

        self.last_caption = candidate
        return candidate


def format_caption(text: str, when: Optional[datetime] = None) -> str:
    timestamp = (when or datetime.now()).strftime("%H:%M:%S")
    return f"[{timestamp}] {text}"


class CaptionPrinter:
    def __init__(self) -> None:
        try:
            from rich.console import Console
        except Exception:
            self.console = None
        else:
            self.console = Console()

    def print(self, text: str) -> None:
        rendered = format_caption(text)
        if self.console is None:
            print(rendered, flush=True)
        else:
            self.console.print(rendered, style="bold cyan")
