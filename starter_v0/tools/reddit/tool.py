from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def search_reddit(
    query: str = "",
    max_results: int = 10,
    sort: str = "relevance",
    timeframe: str = "all",
    content_type: str = "posts",
) -> dict[str, Any]:
    try:
        if not query:
            return {"tool": "reddit", "error": "missing_query", "message": "Query is required"}
        api_key = os.getenv("APIFY_API_KEY")
        if not api_key:
            raise RuntimeError("Missing APIFY_API_KEY env var")
        run_input = {
            "query": query,
            "maxResults": min(max_results, 100),
            "sort": sort,
            "timeframe": timeframe,
            "contentType": content_type,
            "includeBodyText": True,
        }
        resp = requests.post(
            "https://api.apify.com/v2/acts/datara~reddit-search-scraper/run-sync-get-dataset-items",
            params={"token": api_key},
            json=run_input,
            timeout=120,
        )
        resp.raise_for_status()
        raw_items = resp.json()
        items = []
        for item in raw_items[:max_results]:
            items.append({
                "title": item.get("title") or "",
                "url": item.get("url") or item.get("postUrl") or "",
                "source": f"r/{item.get('subreddit', '')}",
                "summary": (item.get("bodyText") or item.get("title") or "")[:500],
                "score": item.get("score", 0),
                "comments": item.get("numComments", 0),
                "author": item.get("author") or "",
                "created": item.get("createdAt") or "",
            })
        return {
            "tool": "reddit",
            "query": query,
            "items": items,
            "count": len(items),
        }
    except Exception as exc:
        return err("reddit", exc)
