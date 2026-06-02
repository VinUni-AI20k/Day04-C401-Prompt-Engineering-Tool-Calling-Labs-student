from __future__ import annotations

import urllib.parse
from typing import Any

import requests

from tools._shared import TIMEOUT


def search_wikipedia(query: str = "", limit: int = 3) -> dict[str, Any]:
    """
    Search Wikipedia for a topic and retrieve page summaries or search results.
    
    Args:
        query: The search term or topic.
        limit: Maximum number of search results to return if direct match is not found.
        
    Returns:
        Dict containing Wikipedia articles and summaries.
    """
    if not query:
        return {
            "tool": "wikipedia",
            "status": "error",
            "message": "Query parameter is required"
        }
        
    headers = {
        "User-Agent": "AI20k-Day04-Research-Agent/1.0 (educational lab; contact: local)"
    }
    
    try:
        # Step 1: Use OpenSearch to search for pages matching the query
        search_query = urllib.parse.quote(query)
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_query}&limit={limit}&namespace=0&format=json"
        
        response = requests.get(search_url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # OpenSearch returns: [query, [titles], [descriptions], [urls]]
        if not data or len(data) < 4 or not data[1]:
            return {
                "tool": "wikipedia",
                "status": "success",
                "query": query,
                "results": [],
                "message": f"No Wikipedia articles found for '{query}'"
            }
            
        titles = data[1]
        urls = data[3]
        results = []
        
        # Step 2: Fetch specific summary for the top result or all matching results
        for idx, (title, url) in enumerate(zip(titles, urls)):
            if idx >= limit:
                break
                
            try:
                title_encoded = urllib.parse.quote(title)
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title_encoded}"
                sum_resp = requests.get(summary_url, headers=headers, timeout=TIMEOUT)
                
                if sum_resp.status_code == 200:
                    sum_data = sum_resp.json()
                    results.append({
                        "title": title,
                        "url": url,
                        "summary": sum_data.get("extract", ""),
                        "description": sum_data.get("description", ""),
                        "thumbnail": sum_data.get("thumbnail", {}).get("source", "")
                    })
                else:
                    results.append({
                        "title": title,
                        "url": url,
                        "summary": data[2][idx] if idx < len(data[2]) else "",
                        "description": ""
                    })
            except Exception:
                results.append({
                    "title": title,
                    "url": url,
                    "summary": data[2][idx] if idx < len(data[2]) else "",
                    "description": ""
                })
                
        return {
            "tool": "wikipedia",
            "status": "success",
            "query": query,
            "results": results,
            "message": f"Found {len(results)} articles for '{query}'"
        }
        
    except requests.exceptions.RequestException as exc:
        return {
            "tool": "wikipedia",
            "status": "error",
            "error_type": "network_error",
            "message": f"Network error while calling Wikipedia: {exc}"
        }
    except Exception as exc:
        return {
            "tool": "wikipedia",
            "status": "error",
            "error_type": "unknown_error",
            "message": f"Unexpected error: {exc}"
        }
