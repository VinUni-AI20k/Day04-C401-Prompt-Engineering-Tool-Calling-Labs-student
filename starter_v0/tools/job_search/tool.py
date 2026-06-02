from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _jsearch_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_JSEARCH_HOST", "jsearch.p.rapidapi.com")

    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")

    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={
            "x-rapidapi-key": key,
            "x-rapidapi-host": host,
        },
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def _job_item(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": raw.get("job_title", ""),
        "company": raw.get("employer_name", ""),
        "location": ", ".join(
            filter(
                None,
                [
                    raw.get("job_city"),
                    raw.get("job_country"),
                ],
            )
        ),
        "url": raw.get("job_apply_link", ""),
        "source": raw.get("employer_name", ""),
        "date": raw.get("job_posted_at_datetime_utc"),
        "summary": raw.get("job_description", "")[:500],
    }


def _jobs_from(data: dict[str, Any], limit: int = 5):
    items = data.get("data", [])
    return [_job_item(x) for x in items[:limit]]


def search_jobs_tool(
    query: str,
    limit: int = 5,
) -> dict[str, Any]:

    try:
        data = _jsearch_get(
            "/search",
            {
                "query": query,
                "page": 1,
                "num_pages": 1,
            },
        )

        return {
            "tool": "search_jobs",
            "query": query,
            "items": _jobs_from(data, limit),
        }

    except Exception as exc:
        return {
            "tool": "search_jobs",
            "error": str(exc),
        }

