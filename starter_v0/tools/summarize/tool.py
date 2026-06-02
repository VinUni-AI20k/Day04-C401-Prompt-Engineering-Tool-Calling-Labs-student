from __future__ import annotations

import re
from typing import Any


def summarize_text(text: str = "", max_sentences: int = 3, language: str = "auto") -> dict[str, Any]:
    if not text or not text.strip():
        return {"tool": "summarize_text", "error": "ValueError", "message": "text is required"}
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if s.strip()]
    selected = sentences[: max(1, int(max_sentences))]
    summary = " ".join(selected)
    return {
        "tool": "summarize_text",
        "summary": summary,
        "original_sentences": len(sentences),
        "summary_sentences": len(selected),
        "language": language,
    }
