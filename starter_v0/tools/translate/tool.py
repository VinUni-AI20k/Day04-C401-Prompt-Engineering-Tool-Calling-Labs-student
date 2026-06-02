from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


def translate_text(text: str = "", target_lang: str = "en", source_lang: str = "auto") -> dict[str, Any]:
    if not text or not text.strip():
        return {"tool": "translate_text", "error": "ValueError", "message": "text is required"}
    try:
        lang_pair = f"{source_lang}|{target_lang}" if source_lang != "auto" else f"auto|{target_lang}"
        url = f"https://api.mymemory.translated.net/get?q={quote(text)}&langpair={lang_pair}"
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        return {
            "tool": "translate_text",
            "original": text,
            "translated": translated,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
    except Exception as exc:
        return err("translate_text", exc)
