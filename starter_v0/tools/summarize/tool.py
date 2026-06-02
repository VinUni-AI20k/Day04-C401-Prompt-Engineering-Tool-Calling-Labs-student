from __future__ import annotations

import re
from collections import Counter
from typing import Any


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _word_freq(text: str) -> Counter[str]:
    words = re.findall(r"[a-zA-ZÀ-ỹ]+", text.lower())
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                 "have", "has", "had", "do", "does", "did", "will", "would", "could",
                 "should", "may", "might", "shall", "can", "need", "dare", "ought",
                 "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
                 "as", "into", "through", "during", "before", "after", "above", "below",
                 "between", "out", "off", "over", "under", "again", "further", "then",
                 "once", "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
                 "neither", "each", "every", "all", "any", "few", "more", "most", "other",
                 "some", "such", "no", "only", "own", "same", "than", "too", "very",
                 "và", "của", "là", "cho", "với", "từ", "được", "này", "đó", "một",
                 "các", "những", "không", "có", "đã", "đang", "sẽ", "hay", "hoặc"}
    return Counter(w for w in words if w not in stopwords and len(w) > 2)


def _score_sentences(sentences: list[str], freq: Counter[str]) -> list[tuple[int, float]]:
    scores = []
    for i, sent in enumerate(sentences):
        words = re.findall(r"[a-zA-ZÀ-ỹ]+", sent.lower())
        score = sum(freq.get(w, 0) for w in words)
        if i < 3:
            score *= 1.5
        scores.append((i, score))
    return scores


def summarize_text(text: str = "", max_sentences: int = 5) -> dict[str, Any]:
    try:
        if not text:
            return {"tool": "summarize", "error": "empty_text", "message": "Text is required"}
        max_sentences = max(1, min(max_sentences, 10))
        sentences = _split_sentences(text)
        if len(sentences) <= max_sentences:
            return {
                "tool": "summarize",
                "summary": text,
                "original_length": len(text),
                "summary_length": len(text),
                "sentences_count": len(sentences),
            }
        freq = _word_freq(text)
        scored = _score_sentences(sentences, freq)
        top = sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]
        top.sort(key=lambda x: x[0])
        summary = " ".join(sentences[i] for i, _ in top)
        return {
            "tool": "summarize",
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "sentences_count": len(top),
        }
    except Exception as exc:
        return {"tool": "summarize", "error": type(exc).__name__, "message": str(exc)}
