from __future__ import annotations

import re
from typing import Any

POSITIVE_EN = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome", "love",
    "happy", "joy", "beautiful", "perfect", "best", "brilliant", "outstanding", "superb",
    "nice", "pleased", "glad", "excited", "thankful", "grateful", "impressive", "remarkable",
    "success", "win", "victory", "celebrate", "recommend", "enjoy", "delightful", "pleasant",
}

NEGATIVE_EN = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "angry", "sad", "ugly",
    "poor", "disappointing", "frustrating", "annoying", "painful", "suffering", "failure",
    "problem", "issue", "error", "bug", "broken", "crash", "fail", "lose", "loss",
    "danger", "risk", "threat", "attack", "disaster", "crisis", "war", "death",
}

POSITIVE_VI = {
    "tốt", "hay", "giỏi", "đẹp", "tuyệt", "xuất sắc", "tuyệt vời", "vui", "hạnh phúc",
    "thành công", "thắng", "chiến thắng", "ấn tượng", "đáng chú ý", "hoàn hảo", "tốt nhất",
}

NEGATIVE_VI = {
    "tệ", "xấu", "kém", "dở", "tồi", "thất bại", "buồn", "giận", "ghét",
    "vấn đề", "lỗi", "hỏng", "crash", "nguy hiểm", "rủi ro", "khủng hoảng", "chiến tranh",
}


def _analyze(text: str) -> dict[str, Any]:
    text_lower = text.lower()
    words = set(re.findall(r"[a-zA-ZÀ-ỹ]+", text_lower))
    pos_en = words & POSITIVE_EN
    neg_en = words & NEGATIVE_EN
    pos_vi = {w for w in POSITIVE_VI if w in text_lower}
    neg_vi = {w for w in NEGATIVE_VI if w in text_lower}
    positive = pos_en | pos_vi
    negative = neg_en | neg_vi
    pos_count = len(positive)
    neg_count = len(negative)
    total = pos_count + neg_count
    if total == 0:
        return {"sentiment": "neutral", "score": 0.5, "positive_words": [], "negative_words": []}
    score = pos_count / total
    if score > 0.6:
        sentiment = "positive"
    elif score < 0.4:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {
        "sentiment": sentiment,
        "score": round(score, 2),
        "positive_words": sorted(positive)[:10],
        "negative_words": sorted(negative)[:10],
    }


def analyze_sentiment(text: str = "") -> dict[str, Any]:
    try:
        if not text:
            return {"tool": "sentiment", "error": "empty_text", "message": "Text is required"}
        result = _analyze(text)
        return {"tool": "sentiment", "text_preview": text[:200], **result}
    except Exception as exc:
        return {"tool": "sentiment", "error": type(exc).__name__, "message": str(exc)}
