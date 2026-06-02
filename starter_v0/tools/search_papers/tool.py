from __future__ import annotations

import os
import re
import time
import xml.etree.ElementTree as ET
from typing import Any

import requests

from tools._shared import TIMEOUT, err


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_MIN_INTERVAL_SECONDS = 3.0
_last_arxiv_request_at = 0.0


def _arxiv_user_agent() -> str:
    return os.getenv("ARXIV_USER_AGENT", "AI20k-Day04-Research-Agent/1.0 (educational lab; contact: local)")


def _rate_limit_arxiv() -> None:
    global _last_arxiv_request_at
    elapsed = time.monotonic() - _last_arxiv_request_at
    if elapsed < ARXIV_MIN_INTERVAL_SECONDS:
        time.sleep(ARXIV_MIN_INTERVAL_SECONDS - elapsed)
    _last_arxiv_request_at = time.monotonic()


def _arxiv_get(url: str, *, params: dict[str, Any] | None = None) -> requests.Response:
    last_response: requests.Response | None = None
    for attempt in range(3):
        _rate_limit_arxiv()
        response = requests.get(url, params=params, headers={"User-Agent": _arxiv_user_agent()}, timeout=TIMEOUT)
        last_response = response
        if response.status_code != 429:
            return response
        time.sleep(3 * (attempt + 1))
    assert last_response is not None
    return last_response


def _arxiv_search_query(query: str) -> str:
    cleaned = " ".join((query or "").split())
    if ":" in cleaned:
        return cleaned
    terms = [term for term in re.findall(r"[A-Za-z0-9_\\-]+", cleaned) if len(term) > 1]
    return " AND ".join(f"all:{term}" for term in terms[:8]) or cleaned


def _arxiv_id(value: str) -> str:
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", value or "")
    return match.group(1) if match else ""


def _entry_text(entry: ET.Element, path: str, namespaces: dict[str, str]) -> str:
    node = entry.find(path, namespaces)
    return (node.text or "").strip() if node is not None and node.text else ""


def arxiv_search(query: str = "", max_results: int = 5, sort_by: str = "relevance") -> dict[str, Any]:
    try:
        max_results = max(1, min(int(max_results or 5), 10))
        sort_by = sort_by if sort_by in {"relevance", "lastUpdatedDate", "submittedDate"} else "relevance"
        params = {
            "search_query": _arxiv_search_query(query),
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": "descending",
        }
        response = _arxiv_get(ARXIV_API_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        namespaces = {
            "atom": "http://www.w3.org/2005/Atom",
            "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        total_node = root.find(".//opensearch:totalResults", namespaces)
        entries: list[dict[str, Any]] = []
        for entry in root.findall(".//atom:entry", namespaces):
            abs_url = _entry_text(entry, "./atom:id", namespaces)
            arxiv_id = _arxiv_id(abs_url)
            links = [{"rel": link.get("rel"), "href": link.get("href"), "title": link.get("title")} for link in entry.findall("./atom:link", namespaces)]
            pdf_url = next((link["href"] for link in links if link.get("title") == "pdf"), f"https://arxiv.org/pdf/{arxiv_id}.pdf")
            primary = entry.find("./arxiv:primary_category", namespaces)
            summary = _entry_text(entry, "./atom:summary", namespaces).replace("\n", " ")
            entries.append({
                "arxiv_id": arxiv_id,
                "title": _entry_text(entry, "./atom:title", namespaces).replace("\n", " "),
                "summary": " ".join(summary.split()),
                "authors": [_entry_text(author, "./atom:name", namespaces) for author in entry.findall("./atom:author", namespaces)],
                "published": _entry_text(entry, "./atom:published", namespaces),
                "updated": _entry_text(entry, "./atom:updated", namespaces),
                "url": abs_url,
                "pdf_url": pdf_url,
                "source": "arxiv.org",
                "primary_category": primary.get("term") if primary is not None else None,
                "categories": [cat.get("term") for cat in entry.findall("./atom:category", namespaces)],
            })
        return {
            "tool": "arxiv_search",
            "query": query,
            "api_query": params["search_query"],
            "total_results": int(total_node.text) if total_node is not None and total_node.text else None,
            "items": entries,
            "rate_limit_note": "arXiv may return 429 if called too frequently; this tool waits at least 3 seconds between requests in-process.",
        }
    except Exception as exc:
        return err("arxiv_search", exc)

