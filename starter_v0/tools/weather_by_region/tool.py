from __future__ import annotations

import os
from typing import Any
import requests

from tools._shared import TIMEOUT, err
from tools.lookup.tool import web_search


def get_weather_by_region(region: str = "") -> dict[str, Any]:
    """
    Get current weather and short-term forecasts for a specified location.
    If the API call fails or key is missing, falls back to web search.
    """
    if not region:
        return {
            "tool": "weather_by_region",
            "error": "ValueError",
            "message": "Region is required but was not provided."
        }

    # 1. Try to use WeatherAPI
    api_key = os.getenv("WEATHER_API_KEY")
    if api_key:
        try:
            response = requests.get(
                "https://api.weatherapi.com/v1/forecast.json",
                params={"key": api_key, "q": region, "days": 3, "aqi": "no", "alerts": "no"},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "tool": "weather_by_region",
                "region": data.get("location", {}).get("name", region),
                "temperature": data.get("current", {}).get("temp_c"),
                "condition": data.get("current", {}).get("condition", {}).get("text"),
                "forecast": [
                    {
                        "date": day.get("date"),
                        "avgtemp_c": day.get("day", {}).get("avgtemp_c"),
                        "condition": day.get("day", {}).get("condition", {}).get("text"),
                    }
                    for day in data.get("forecast", {}).get("forecastday", [])
                ],
                "source": "WeatherAPI"
            }
        except Exception as exc:
            # If WeatherAPI request failed, we fall back to web search below
            pass

    # 2. Fallback to Web Search
    try:
        search_query = f"current weather and forecast in {region}"
        search_res = web_search(query=search_query, topic="general", timeframe="day", max_results=3)
        
        if "error" in search_res:
            raise RuntimeError(f"Web search fallback failed: {search_res.get('message')}")
            
        items = search_res.get("items", [])
        
        # Synthesize a response from search results
        condition = "Refer to web search results"
        temperature = "N/A"
        
        if items:
            # Use the snippet/summary from the top result as condition summary
            condition = items[0].get("summary", "Refer to web search results")
            
        return {
            "tool": "weather_by_region",
            "region": region,
            "temperature": temperature,
            "condition": condition,
            "web_search_results": items,
            "source": "Tavily Web Search (Fallback)"
        }
    except Exception as exc:
        return err("weather_by_region", exc)
