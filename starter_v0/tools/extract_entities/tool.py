from __future__ import annotations

import re
from typing import Any


def extract_entities(text: str = "", entity_types: list[str] | None = None) -> dict[str, Any]:
    if not text or not text.strip():
        return {"tool": "extract_entities", "error": "ValueError", "message": "text is required"}

    want = set(entity_types) if entity_types else {"mentions", "hashtags", "urls", "emails"}
    result: dict[str, Any] = {"tool": "extract_entities", "text_length": len(text)}

    if "mentions" in want:
        result["mentions"] = re.findall(r"@(\w{1,50})", text)
    if "hashtags" in want:
        result["hashtags"] = re.findall(r"#(\w+)", text)
    if "urls" in want:
        result["urls"] = re.findall(r"https?://[^\s\"'>]+", text)
    if "emails" in want:
        result["emails"] = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)

    return result
