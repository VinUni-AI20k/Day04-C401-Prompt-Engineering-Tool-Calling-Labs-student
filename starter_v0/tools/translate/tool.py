from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def translate_text(text: str = "", source_lang: str = "auto", target_lang: str = "en") -> dict[str, Any]:
    try:
        if not text:
            return {"tool": "translate", "error": "empty_text", "message": "Text is required"}
        if source_lang == "auto":
            source_lang = ""
        lang_pair = f"{source_lang}|{target_lang}" if source_lang else target_lang
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text[:500], "langpair": lang_pair},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        if data.get("responseStatus") != 200:
            return {"tool": "translate", "error": "api_error", "message": data.get("responseDetails", "Unknown error")}
        return {
            "tool": "translate",
            "original_text": text,
            "translated_text": translated,
            "source_lang": source_lang or "auto",
            "target_lang": target_lang,
        }
    except Exception as exc:
        return err("translate", exc)
