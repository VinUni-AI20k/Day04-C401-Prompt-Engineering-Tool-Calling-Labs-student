from __future__ import annotations

import re
from typing import Any


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text.lower())).strip()


def _similarity(a: str, b: str) -> float:
    """Jaccard similarity on word sets."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def dedupe_items(
    items: list[dict[str, Any]] | None = None,
    key: str = "summary",
    threshold: float = 0.6,
) -> dict[str, Any]:
    """Remove near-duplicate items based on text similarity of a chosen field."""
    items = items or []
    if not items:
        return {"tool": "dedupe_items", "unique": [], "removed_count": 0, "original_count": 0}

    threshold = max(0.1, min(float(threshold or 0.6), 1.0))
    unique: list[dict[str, Any]] = []
    unique_texts: list[str] = []
    removed = 0

    for item in items:
        text = _normalize(str(item.get(key, "") or item.get("title", "") or ""))
        if not text:
            unique.append(item)
            unique_texts.append("")
            continue

        is_dup = False
        for existing_text in unique_texts:
            if existing_text and _similarity(text, existing_text) >= threshold:
                is_dup = True
                removed += 1
                break

        if not is_dup:
            unique.append(item)
            unique_texts.append(text)

    return {
        "tool": "dedupe_items",
        "unique": unique,
        "removed_count": removed,
        "original_count": len(items),
        "unique_count": len(unique),
        "threshold": threshold,
        "key": key,
    }
