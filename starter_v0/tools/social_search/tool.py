from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _apify_search(query: str, search_type: str, limit: int) -> dict[str, Any]:
    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing APIFY_API_KEY env var")
    search_type_map = {"Latest": "Latest", "Top": "Top"}
    resp = requests.post(
        "https://api.apify.com/v2/acts/powerai~twitter-search-scraper/run-sync-get-dataset-items",
        params={"token": api_key},
        json={"query": query, "searchType": search_type_map.get(search_type, "Latest"), "maxResults": max(limit, 15)},
        timeout=120,
    )
    resp.raise_for_status()
    raw_items = resp.json()
    items = []
    for raw in raw_items[:limit]:
        handle = raw.get("screen_name") or ""
        tweet_id = raw.get("tweet_id") or raw.get("id") or ""
        text = (raw.get("text") or "").strip()
        items.append({
            "title": text.split("\n")[0][:120],
            "summary": text,
            "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
            "source": f"@{handle}" if handle else "x.com",
            "date": raw.get("created_at"),
            "metrics": {
                "favorites": raw.get("favorites") or 0,
                "retweets": raw.get("retweets") or 0,
                "views": raw.get("views") or 0,
            },
        })
    return {"tool": "search_tweets", "query": query, "search_type": search_type, "items": items}


def _rapid_search(query: str, search_type: str, limit: int) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter241.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")
    resp = requests.get(
        f"https://{host}/search.php",
        params={"query": query, "search_type": search_type},
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    raw_items = data.get("timeline") or data.get("tweets") or []
    items = []
    for raw in raw_items:
        if not (raw.get("tweet_id") or raw.get("id")):
            continue
        handle = raw.get("screen_name") or (raw.get("author") or {}).get("screen_name") or ""
        tweet_id = raw.get("tweet_id") or raw.get("id") or ""
        text = (raw.get("text") or "").strip()
        items.append({
            "title": text.split("\n")[0][:120],
            "summary": text,
            "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
            "source": f"@{handle}" if handle else "x.com",
            "date": raw.get("created_at"),
            "metrics": {"favorites": raw.get("favorites"), "retweets": raw.get("retweets"), "views": raw.get("views")},
        })
    return {"tool": "search_tweets", "query": query, "search_type": search_type, "items": items[:limit]}


def search_tweets(query: str = "", search_type: str = "Latest", limit: int = 5) -> dict[str, Any]:
    try:
        if not query:
            return {"tool": "search_tweets", "error": "missing_query", "message": "Query is required"}
        try:
            return _apify_search(query, search_type, limit)
        except Exception:
            return _rapid_search(query, search_type, limit)
    except Exception as exc:
        return err("search_tweets", exc)
