"""Immediate no-setup translation backend for display testing."""

from __future__ import annotations


class MockTranslator:
    PHRASES = {
        "where is the train station?": "火车站在哪里？",
        "i would like a cup of coffee.": "我想要一杯咖啡。",
        "please speak more slowly.": "请说慢一点。",
        "how much does this cost?": "这个多少钱？",
        "can you write that down?": "你能把那个写下来吗？",
        "thank you very much.": "非常感谢。",
    }

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
        normalized = " ".join(text.strip().lower().split())
        return self.PHRASES.get(normalized, f"[mock zh] {text.strip()}")
