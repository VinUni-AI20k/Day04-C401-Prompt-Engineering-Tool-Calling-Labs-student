from __future__ import annotations

import os
from typing import Any
import requests
from .._shared import TIMEOUT, err

def _twitter_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")
    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()

def get_twitter_trends() -> dict[str, Any]:
    """
    Fetches the current trending topics on Twitter/X globally.
    """
    try:
        # Based on typical RapidAPI Twitter API structure for trends
        data = _twitter_get("/trends.php", {})
        
        # Format the trends for the agent
        raw_trends = data.get("trends", [])
        formatted_trends = []
        for trend in raw_trends:
            formatted_trends.append({
                "name": trend.get("name"),
                "query": trend.get("query"),
                "tweet_volume": trend.get("tweet_volume")
            })
            
        return {
            "tool": "twitter_trends",
            "status": "success",
            "trends": formatted_trends[:15] # Return top 15 trends
        }
    except Exception as exc:
        return err("twitter_trends", exc)
