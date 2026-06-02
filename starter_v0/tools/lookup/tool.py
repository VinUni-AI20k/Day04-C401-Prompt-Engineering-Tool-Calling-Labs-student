from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

VN_NEWS_DOMAINS = [
    "vnexpress.net",
    "dantri.com.vn",
    "tuoitre.vn",
    "vietnamnet.vn",
    "thanhnien.vn",
    "nld.com.vn",
    "plo.vn",
    "vietnamplus.vn",
    "baomoi.com",
    "kenh14.vn",
]

VN_KEYWORDS = re.compile(
    r"(việt nam|vietnam|vn|hà nội|hanoi|hồ chí minh|ho chi minh|đà nẵng|da nang|"
    r"thủ tướng|chủ tịch|bộ trưởng|quốc hội|nghị định|thông tư|"
    r"tin tức|tin mới|bản tin|hôm nay|hôm qua|tuần này)",
    re.IGNORECASE,
)


def _has_vietnamese_context(query: str, topic: str) -> bool:
    if topic == "news" and VN_KEYWORDS.search(query):
        return True
    return False


def web_search(query: str = "", topic: str = "general", timeframe: str | None = "week", max_results: int = 5) -> dict[str, Any]:
    try:
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY env var")
        body: dict[str, Any] = {"query": query, "topic": topic, "max_results": int(max_results or 5), "search_depth": "basic"}
        if timeframe:
            body["time_range"] = timeframe
        if _has_vietnamese_context(query, topic):
            body["include_domains"] = VN_NEWS_DOMAINS
        response = requests.post(
            "https://api.tavily.com/search",
            json=body,
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": domain(item.get("url", "")),
            "summary": item.get("content"),
            "score": item.get("score"),
        } for item in data.get("results", [])]
        return {"tool": "web_search", "query": query, "topic": topic, "timeframe": timeframe, "items": items}
    except Exception as exc:
        return err("web_search", exc)

