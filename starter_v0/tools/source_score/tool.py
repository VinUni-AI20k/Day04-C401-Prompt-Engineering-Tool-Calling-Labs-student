from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from tools._shared import err


HIGH_TRUST_DOMAINS = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "nature.com",
    "science.org",
    "arxiv.org",
    "anthropic.com",
    "openai.com",
    "deepmind.google",
    "microsoft.com",
}

LOW_TRUST_MARKERS = ("blogspot.", "medium.com", "substack.com", "reddit.com", "x.com", "twitter.com")


def score_source(url: str = "", title: str = "", source: str = "") -> dict[str, Any]:
    try:
        parsed = urlparse(url or "")
        domain = parsed.netloc.lower().replace("www.", "") or source.lower().replace("www.", "")
        score = 50
        reasons: list[str] = []

        if parsed.scheme == "https":
            score += 10
            reasons.append("uses_https")
        elif url:
            score -= 10
            reasons.append("not_https")

        if domain in HIGH_TRUST_DOMAINS or any(domain.endswith(f".{item}") for item in HIGH_TRUST_DOMAINS):
            score += 30
            reasons.append("recognized_primary_or_editorial_source")
        elif any(marker in domain for marker in LOW_TRUST_MARKERS):
            score -= 15
            reasons.append("social_or_personal_publishing_domain")

        if title and any(word in title.lower() for word in ("breaking", "exclusive", "shocking", "leak")):
            score -= 5
            reasons.append("sensational_title_marker")

        score = max(0, min(100, score))
        if score >= 80:
            rating = "high"
        elif score >= 55:
            rating = "medium"
        else:
            rating = "low"

        return {
            "tool": "score_source",
            "url": url,
            "domain": domain,
            "source": source,
            "score": score,
            "rating": rating,
            "reasons": reasons,
            "guidance": "Use as a lightweight source-quality signal, not as proof that a claim is true.",
        }
    except Exception as exc:
        return err("score_source", exc)
