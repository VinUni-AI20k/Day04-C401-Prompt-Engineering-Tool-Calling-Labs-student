from __future__ import annotations

import re
from collections import Counter
from typing import Any

from tools._shared import err, fold_text


# Stopwords in English and Vietnamese
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to", "with", "about",
    "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay", "nhu",
    "nen", "the", "thi", "trong", "va", "ve", "voi", "cua", "de", "co", "mot", "nhung", "ra", "ta", "toi", "cac", "la",
    "is", "it", "this", "that", "these", "those", "they", "them", "their", "there", "here", "be", "been", "was", "were",
    "have", "has", "had", "do", "does", "did", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by",
    "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
}

# Positive and Negative Words lexicon for simple sentiment analysis
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "love", "like", "best", "cool", "awesome",
    "perfect", "better", "success", "innovative", "excited", "happy", "win", "breaking", "progress",
    "growth", "growing", "stable", "beautiful", "strong", "easy", "clean", "smart", "helpful", "future",
    "tot", "tuyet", "hay", "thich", "yeu", "dep", "ben", "on", "ok", "phat trien", "thanh cong", "tien bo",
    "vui", "mung", "nhanh", "hieu qua", "on dinh", "manh", "de", "sach", "thong minh", "giup", "tuong lai"
}

NEGATIVE_WORDS = {
    "bad", "worst", "worse", "hate", "dislike", "fail", "failure", "error", "bug", "crash", "slow",
    "delay", "issue", "problem", "broken", "sad", "angry", "terrible", "poor", "difficult", "hard",
    "loss", "lose", "scam", "danger", "risk", "fake", "weak",
    "xau", "te", "do", "ghet", "loi", "hong", "cham", "tre", "van de", "kho", "kho khan", "that bai",
    "mat", "buon", "lua", "nguy hiem", "rui ro", "gia", "yeu"
}

# Fold the lexicons
POSITIVE_WORDS = {fold_text(w) for w in POSITIVE_WORDS}
NEGATIVE_WORDS = {fold_text(w) for w in NEGATIVE_WORDS}


def _extract_texts(data: Any) -> list[str]:
    """
    Recursively extracts string texts from standard data formats.
    """
    texts = []
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            for item in data["items"]:
                texts.extend(_extract_texts(item))
        else:
            for key in ["summary", "content", "title", "text", "description"]:
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    texts.append(val.strip())
            if not texts:
                for k, v in data.items():
                    if isinstance(v, str) and len(v.strip()) > 10:
                        texts.append(v.strip())
                    elif isinstance(v, (list, dict)):
                        texts.extend(_extract_texts(v))
    elif isinstance(data, list):
        for item in data:
            texts.extend(_extract_texts(item))
    elif isinstance(data, str):
        if data.strip():
            texts.append(data.strip())
    return texts


def analyze_trends(data: Any) -> dict[str, Any]:
    """
    Analyze posts or articles to identify trending topics, keywords, and sentiment.
    """
    try:
        texts = _extract_texts(data)
        if not texts:
            return {
                "tool": "trend_analyzer",
                "trend_analysis": {
                    "trending_topics": [],
                    "keywords": [],
                    "sentiment": "Neutral",
                    "sentiment_score": {"positive": 0, "negative": 0},
                    "summary": "No data available to analyze trends."
                }
            }

        # 1. Extract Keywords
        words = []
        for text in texts:
            folded = fold_text(text)
            tokens = re.findall(r"[a-z0-9]+", folded)
            for token in tokens:
                if len(token) > 2 and token not in STOPWORDS:
                    words.append(token)
        
        counter = Counter(words)
        top_k = counter.most_common(8)
        keywords = [k for k, _ in top_k]

        # 2. Analyze Sentiment
        pos_count = 0
        neg_count = 0
        for text in texts:
            folded = fold_text(text)
            tokens = re.findall(r"[a-z0-9]+", folded)
            for token in tokens:
                if token in POSITIVE_WORDS:
                    pos_count += 1
                elif token in NEGATIVE_WORDS:
                    neg_count += 1

        if pos_count > neg_count:
            sentiment = "Positive"
        elif neg_count > pos_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # 3. Create Summary
        kw_str = ", ".join(f"'{k}'" for k in keywords[:5])
        summary = f"Main keywords/topics: {kw_str or 'None'}. Sentiment is {sentiment} (positive: {pos_count}, negative: {neg_count})."

        trend_analysis = {
            "trending_topics": keywords,
            "keywords": keywords,
            "sentiment": sentiment,
            "sentiment_score": {"positive": pos_count, "negative": neg_count},
            "summary": summary
        }

        return {
            "tool": "trend_analyzer",
            "trend_analysis": trend_analysis
        }
    except Exception as exc:
        return err("trend_analyzer", exc)
