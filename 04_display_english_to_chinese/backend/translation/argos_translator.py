"""Argos Translate adapter, used after language packages are installed."""

from __future__ import annotations


class ArgosTranslator:
    def __init__(self) -> None:
        try:
            import argostranslate.translate as translate
        except ImportError as exc:  # pragma: no cover - dependency dependent
            raise RuntimeError(
                "Argos Translate is not installed. Run `pip install -r requirements.txt` "
                "or use TRANSLATOR_BACKEND=mock."
            ) from exc

        self._translate = translate

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
        installed_languages = self._translate.get_installed_languages()
        source = next((lang for lang in installed_languages if lang.code == source_lang), None)
        target = next((lang for lang in installed_languages if lang.code == target_lang), None)
        if source is None or target is None:
            raise RuntimeError(
                "Argos en -> zh package is not installed. Install the language package "
                "or use TRANSLATOR_BACKEND=mock for display-only testing."
            )

        translation = source.get_translation(target)
        if translation is None:
            raise RuntimeError(
                "Argos cannot find an en -> zh translation package. Install it first "
                "or use TRANSLATOR_BACKEND=mock."
            )
        return translation.translate(text)
