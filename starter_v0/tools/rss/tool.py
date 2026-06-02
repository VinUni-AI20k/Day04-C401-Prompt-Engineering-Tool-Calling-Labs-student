from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _clean_xml(text: str) -> str:
    text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)", "&amp;", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def _extract_items_regex(content: str) -> tuple[str, list[dict[str, Any]]]:
    title_match = re.search(r"<channel>.*?<title>(.*?)</title>", content, re.DOTALL)
    feed_title = title_match.group(1).strip() if title_match else ""
    items = []
    for item_match in re.finditer(r"<item>(.*?)</item>", content, re.DOTALL):
        item_content = item_match.group(1)
        title = re.search(r"<title>(.*?)</title>", item_content, re.DOTALL)
        link = re.search(r"<link>(.*?)</link>", item_content, re.DOTALL)
        desc = re.search(r"<description>(.*?)</description>", item_content, re.DOTALL)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", item_content, re.DOTALL)
        items.append({
            "title": title.group(1).strip() if title else "",
            "url": link.group(1).strip() if link else "",
            "summary": desc.group(1).strip() if desc else "",
            "published": pub.group(1).strip() if pub else "",
        })
    return feed_title, items


def _parse_rss(root: ET.Element) -> tuple[str, list[dict[str, Any]]]:
    channel = root.find("channel")
    if channel is None:
        return "", []
    title = (channel.findtext("title") or "").strip()
    items = []
    for item in channel.findall("item"):
        items.append({
            "title": (item.findtext("title") or "").strip(),
            "url": (item.findtext("link") or "").strip(),
            "summary": (item.findtext("description") or "").strip(),
            "published": (item.findtext("pubDate") or "").strip(),
        })
    return title, items


def _parse_atom(root: ET.Element) -> tuple[str, list[dict[str, Any]]]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    title = (root.findtext("atom:title", namespaces=ns) or root.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
    if not title:
        title_el = root.find("{http://www.w3.org/2005/Atom}title")
        title = (title_el.text or "").strip() if title_el is not None else ""
    items = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
        content_el = entry.find("{http://www.w3.org/2005/Atom}content")
        summary = ""
        if summary_el is not None and summary_el.text:
            summary = summary_el.text.strip()
        elif content_el is not None and content_el.text:
            summary = content_el.text.strip()
        published_el = entry.find("{http://www.w3.org/2005/Atom}published")
        if published_el is None:
            published_el = entry.find("{http://www.w3.org/2005/Atom}updated")
        published = (published_el.text or "").strip() if published_el is not None else ""
        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
        entry_title = (title_el.text or "").strip() if title_el is not None else ""
        items.append({
            "title": entry_title,
            "url": link,
            "summary": summary,
            "published": published,
        })
    return title, items


def fetch_rss(url: str = "", max_items: int = 10) -> dict[str, Any]:
    try:
        if not url:
            return {"tool": "rss", "error": "missing_url", "message": "URL is required"}
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "ResearchAgent/1.0"})
        resp.raise_for_status()
        content = resp.text
        try:
            cleaned = _clean_xml(content)
            root = ET.fromstring(cleaned.encode("utf-8"))
            if root.tag == "rss" or root.find("channel") is not None:
                feed_title, items = _parse_rss(root)
            else:
                feed_title, items = _parse_atom(root)
        except ET.ParseError:
            feed_title, items = _extract_items_regex(content)
        items = items[:max_items]
        return {
            "tool": "rss",
            "url": url,
            "feed_title": feed_title,
            "items": items,
            "count": len(items),
        }
    except Exception as exc:
        return err("rss", exc)
