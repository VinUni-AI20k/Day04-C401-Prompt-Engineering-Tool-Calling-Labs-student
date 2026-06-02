from __future__ import annotations

import os
import re
from typing import Any

import requests
from html.parser import HTMLParser

from tools._shared import TIMEOUT, domain, err


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip = False
        self._skip_tags = {"script", "style", "nav", "footer", "header", "aside"}
        self._block_tags = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br", "div", "tr", "td", "th"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags:
            self._skip = False
        if tag in self._block_tags:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = data.strip()
            if text:
                self._parts.append(text + " ")

    def get_text(self) -> str:
        raw = "".join(self._parts)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r" {2,}", " ", raw)
        return raw.strip()


def _extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _fetch_plain(url: str) -> dict[str, Any]:
    resp = requests.get(url, timeout=TIMEOUT, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)",
    })
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    html = resp.text
    title = _extract_title(html)
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.get_text()
    return {"tool": "read_url", "url": url, "items": [{
        "title": title or url,
        "url": url,
        "source": domain(url),
        "summary": text[:4000],
    }]}


def _fetch_firecrawl(url: str, key: str) -> dict[str, Any]:
    response = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        json={"url": url, "formats": ["markdown"]},
        headers={"Authorization": f"Bearer {key}"},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json().get("data", {})
    meta = data.get("metadata", {}) or {}
    return {"tool": "read_url", "url": url, "items": [{
        "title": meta.get("title") or url,
        "url": meta.get("sourceURL") or url,
        "source": domain(url),
        "summary": (data.get("markdown") or "")[:4000],
    }]}


def read_url(url: str = "") -> dict[str, Any]:
    try:
        if not url:
            return {"tool": "read_url", "error": "missing_url", "message": "URL is required"}
        key = os.getenv("FIRECRAWL_API_KEY")
        if key:
            try:
                return _fetch_firecrawl(url, key)
            except Exception:
                pass
        return _fetch_plain(url)
    except Exception as exc:
        return err("read_url", exc)
