from __future__ import annotations

import re
from typing import Any


def summarize_text(
    text: str = "",
    max_sentences: int = 5,
    language: str = "auto",
) -> dict[str, Any]:
    """Extract the most important sentences from a text block using extractive summarization."""
    if not text or not text.strip():
        return {"tool": "summarize_text", "error": "empty_input", "message": "No text provided to summarize."}

    # Split into sentences (handles both English and Vietnamese punctuation)
    sentences = re.split(r'(?<=[.!?。])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return {"tool": "summarize_text", "summary": text.strip(), "sentence_count": 0, "original_length": len(text)}

    # Score sentences by position and keyword density
    word_freq: dict[str, int] = {}
    for sentence in sentences:
        for word in re.findall(r'\w+', sentence.lower()):
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

    scored: list[tuple[float, int, str]] = []
    for idx, sentence in enumerate(sentences):
        words = re.findall(r'\w+', sentence.lower())
        if not words:
            continue
        freq_score = sum(word_freq.get(w, 0) for w in words if len(w) > 2) / len(words)
        # Boost first and last sentences (usually contain key info)
        position_boost = 1.5 if idx == 0 else (1.2 if idx == len(sentences) - 1 else 1.0)
        # Boost longer sentences (more informative) but cap it
        length_boost = min(len(words) / 10.0, 1.5)
        score = freq_score * position_boost * length_boost
        scored.append((score, idx, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    max_sentences = max(1, min(int(max_sentences or 5), len(sentences)))
    top = sorted(scored[:max_sentences], key=lambda x: x[1])  # restore original order
    summary = " ".join(item[2] for item in top)

    return {
        "tool": "summarize_text",
        "summary": summary,
        "sentence_count": len(top),
        "original_sentences": len(sentences),
        "original_length": len(text),
        "summary_length": len(summary),
    }
