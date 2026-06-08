"""Optional text translation backends."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import random
from typing import Any, Optional


BAIDU_ENDPOINT = "https://fanyi-api.baidu.com/api/trans/vip/translate"


class TextTranslationError(RuntimeError):
    """Raised when text translation fails."""


@dataclass(frozen=True)
class BaiduConfig:
    app_id: str
    secret_key: str
    endpoint: str = BAIDU_ENDPOINT
    timeout_seconds: float = 8.0

    @classmethod
    def from_env(cls) -> "BaiduConfig":
        try:
            from dotenv import load_dotenv
        except ImportError:
            load_dotenv = None
        if load_dotenv is not None:
            load_dotenv()

        app_id = os.getenv("BAIDU_TRANSLATE_APP_ID", "").strip()
        secret_key = os.getenv("BAIDU_TRANSLATE_SECRET_KEY", "").strip()
        if not app_id or not secret_key:
            raise TextTranslationError(
                "Baidu mode requires BAIDU_TRANSLATE_APP_ID and "
                "BAIDU_TRANSLATE_SECRET_KEY. Export them or add them to .env."
            )
        return cls(app_id=app_id, secret_key=secret_key)


class BaiduTranslator:
    """Baidu text translation API adapter."""

    def __init__(self, config: BaiduConfig, session: Optional[Any] = None) -> None:
        self.config = config
        self.session = session

    @classmethod
    def from_env(cls) -> "BaiduTranslator":
        return cls(BaiduConfig.from_env())

    def sign(self, text: str, salt: str) -> str:
        raw = f"{self.config.app_id}{text}{salt}{self.config.secret_key}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def translate(self, text: str, source_lang: str = "zh", target_lang: str = "en") -> str:
        query = text.strip()
        if not query:
            return ""

        salt = str(random.randint(100000, 999999999))
        payload = {
            "q": query,
            "from": source_lang,
            "to": target_lang,
            "appid": self.config.app_id,
            "salt": salt,
            "sign": self.sign(query, salt),
        }
        session = self.session or self._requests()
        try:
            response = session.post(
                self.config.endpoint,
                data=payload,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise TextTranslationError(f"Baidu request failed: {exc}") from exc
        if "error_code" in data:
            raise TextTranslationError(
                f"Baidu error {data.get('error_code')}: {data.get('error_msg', 'unknown error')}"
            )
        results = data.get("trans_result") or []
        translated = " ".join(str(item.get("dst", "")).strip() for item in results).strip()
        if not translated:
            raise TextTranslationError("Baidu response did not include translated text.")
        return translated

    @staticmethod
    def _requests() -> Any:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover - install dependent
            raise TextTranslationError(
                "Baidu mode requires requests. Run `pip install -r requirements.txt`."
            ) from exc
        return requests
