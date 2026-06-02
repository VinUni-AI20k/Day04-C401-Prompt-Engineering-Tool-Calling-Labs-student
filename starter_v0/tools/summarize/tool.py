from __future__ import annotations

import re
from typing import Any


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences. Handles Vietnamese and English punctuation."""
    # Split on sentence-ending punctuation followed by whitespace or end of string
    raw = re.split(r'(?<=[.!?؟])\s+', text.strip())
    # Also split on Vietnamese sentence endings if not already caught
    sentences: list[str] = []
    for chunk in raw:
        # Further split on newlines that act as sentence boundaries
        for line in chunk.split("\n"):
            line = line.strip()
            if line:
                sentences.append(line)
    return sentences


def summarize_text(text: str = "", max_sentences: int = 5, max_chars: int = 500) -> dict[str, Any]:
    """Summarize a long text by extracting the most important sentences."""
    if not text or not text.strip():
        return {
            "tool": "summarize",
            "error": "empty_input",
            "message": "No text provided to summarize.",
        }

    text = text.strip()
    original_length = len(text)

    # If text is already short enough, return as-is
    if original_length <= max_chars:
        return {
            "tool": "summarize",
            "summary": text,
            "original_length": original_length,
            "summary_length": original_length,
            "sentences_used": len(_split_sentences(text)),
        }

    sentences = _split_sentences(text)

    # If only 1-2 sentences, just truncate
    if len(sentences) <= 2:
        truncated = text[:max_chars]
        if len(text) > max_chars:
            truncated = truncated.rsplit(" ", 1)[0] + "..."
        return {
            "tool": "summarize",
            "summary": truncated,
            "original_length": original_length,
            "summary_length": len(truncated),
            "sentences_used": 1,
        }

    # Score sentences by position (first and last sentences are usually important)
    # and by length (very short sentences are often less important)
    scored: list[tuple[float, int, str]] = []
    for i, sentence in enumerate(sentences):
        score = 0.0
        # Position bonus: first sentence gets highest, last gets medium
        if i == 0:
            score += 3.0
        elif i == 1:
            score += 2.0
        elif i == len(sentences) - 1:
            score += 1.5
        elif i < len(sentences) * 0.3:
            score += 1.0

        # Length bonus: prefer medium-length sentences
        word_count = len(sentence.split())
        if 10 <= word_count <= 40:
            score += 1.0
        elif word_count < 5:
            score -= 1.0

        scored.append((score, i, sentence))

    # Sort by score descending, then by position ascending for stability
    scored.sort(key=lambda x: (-x[0], x[1]))

    # Pick top sentences, then restore original order
    selected: list[tuple[int, str]] = []
    for score, idx, sentence in scored:
        selected.append((idx, sentence))
        # Check if we've hit the char limit
        total = sum(len(s) for _, s in selected)
        if total >= max_chars:
            break
        if len(selected) >= max_sentences:
            break

    # Restore original order
    selected.sort(key=lambda x: x[0])

    summary = " ".join(s for _, s in selected)

    # Final truncation if still too long
    if len(summary) > max_chars:
        summary = summary[:max_chars].rsplit(" ", 1)[0] + "..."

    return {
        "tool": "summarize",
        "summary": summary,
        "original_length": original_length,
        "summary_length": len(summary),
        "sentences_used": len(selected),
    }
