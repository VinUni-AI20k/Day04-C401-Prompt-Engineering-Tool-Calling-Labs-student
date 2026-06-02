from __future__ import annotations

import urllib.parse
from typing import Any

import requests

from tools._shared import TIMEOUT


def search_github(query: str = "", limit: int = 5) -> dict[str, Any]:
    """
    Search GitHub repositories matching the query.
    
    Args:
        query: Search keywords (e.g., "react", "machine learning").
        limit: Max repositories to return (default 5, max 10).
        
    Returns:
        Dict containing repository list with stars, forks, and links.
    """
    if not query:
        return {
            "tool": "github_search",
            "status": "error",
            "message": "Query parameter is required"
        }
        
    headers = {
        "User-Agent": "AI20k-Day04-Research-Agent/1.0 (educational lab; contact: local)",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Optional token support if user configured it
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc"
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 403:
            # Handle rate limiting elegantly
            return {
                "tool": "github_search",
                "status": "error",
                "error_type": "rate_limited",
                "message": "GitHub API rate limit exceeded. Please try again later or add a GITHUB_TOKEN.",
                "suggestion": "If you are running search frequently, GitHub restricts unauthenticated API calls."
            }
            
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        results = []
        
        for idx, item in enumerate(items):
            if idx >= limit:
                break
            results.append({
                "name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "url": item.get("html_url", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language", "Unknown"),
                "updated_at": item.get("updated_at", "")
            })
            
        return {
            "tool": "github_search",
            "status": "success",
            "query": query,
            "results": results,
            "message": f"Successfully retrieved {len(results)} GitHub repositories for '{query}'"
        }
        
    except requests.exceptions.RequestException as exc:
        return {
            "tool": "github_search",
            "status": "error",
            "error_type": "network_error",
            "message": f"Network error while calling GitHub API: {exc}"
        }
    except Exception as exc:
        return {
            "tool": "github_search",
            "status": "error",
            "error_type": "unknown_error",
            "message": f"Unexpected error: {exc}"
        }

# Ensure os is imported
import os
