from __future__ import annotations

import re
from typing import Any


# Common patterns for entity extraction
_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
_URL_RE = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
_ARXIV_RE = re.compile(r'\d{4}\.\d{4,5}(?:v\d+)?')
_HASHTAG_RE = re.compile(r'#\w+')
_MENTION_RE = re.compile(r'@\w+')
_DATE_RE = re.compile(
    r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|\w+ \d{1,2},? \d{4})\b'
)
_NUMBER_RE = re.compile(r'\b\d+(?:\.\d+)?(?:\s*[%KMBkmb])?\b')


def extract_entities(
    text: str = "",
    entity_types: list[str] | None = None,
) -> dict[str, Any]:
    """Extract named entities and structured data from text using regex patterns."""
    if not text or not text.strip():
        return {"tool": "extract_entities", "error": "empty_input", "message": "No text provided."}

    all_types = {"emails", "urls", "arxiv_ids", "hashtags", "mentions", "dates", "numbers"}
    requested = set(entity_types) if entity_types else all_types

    entities: dict[str, list[str]] = {}

    if "emails" in requested:
        entities["emails"] = list(set(_EMAIL_RE.findall(text)))

    if "urls" in requested:
        entities["urls"] = list(set(_URL_RE.findall(text)))

    if "arxiv_ids" in requested:
        entities["arxiv_ids"] = list(set(_ARXIV_RE.findall(text)))

    if "hashtags" in requested:
        entities["hashtags"] = list(set(_HASHTAG_RE.findall(text)))

    if "mentions" in requested:
        entities["mentions"] = list(set(_MENTION_RE.findall(text)))

    if "dates" in requested:
        entities["dates"] = list(set(_DATE_RE.findall(text)))

    if "numbers" in requested:
        raw_numbers = _NUMBER_RE.findall(text)
        # Dedupe and limit
        entities["numbers"] = list(set(raw_numbers))[:20]

    total = sum(len(v) for v in entities.values())

    return {
        "tool": "extract_entities",
        "entities": entities,
        "total_found": total,
        "entity_types_searched": sorted(requested & all_types),
        "text_length": len(text),
    }
