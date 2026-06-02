from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}


def apify_run(actor_id: str, run_input: dict[str, Any], timeout: int = 120) -> list[dict[str, Any]]:
    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing APIFY_API_KEY env var")
    resp = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items",
        params={"token": api_key},
        json=run_input,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def tweet_item(raw: dict[str, Any]) -> dict[str, Any]:
    handle = raw.get("author", {}).get("userName") or raw.get("screen_name") or ""
    tweet_id = raw.get("id") or raw.get("tweet_id") or ""
    text = (raw.get("text") or raw.get("full_text") or "").strip()
    return {
        "title": text.split("\n")[0][:120],
        "summary": text,
        "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
        "source": f"@{handle}" if handle else "x.com",
        "date": raw.get("createdAt") or raw.get("created_at"),
        "metrics": {
            "favorites": raw.get("likeCount") or raw.get("favorites") or 0,
            "retweets": raw.get("retweetCount") or raw.get("retweets") or 0,
            "views": raw.get("viewCount") or raw.get("views") or 0,
        },
    }
