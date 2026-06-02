from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, urlunparse

from tools._shared import domain, err


def _normalize_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    normalized_path = parsed.path.rstrip("/")
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower().removeprefix("www."),
        normalized_path,
        "",
        parsed.query,
        "",
    ))


def _is_valid_web_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_sources(items: list[dict[str, Any]] | None = None, min_sources: int = 2) -> dict[str, Any]:
    try:
        source_items = items or []
        normalized_counts: dict[str, int] = {}
        for item in source_items:
            normalized = _normalize_url(str(item.get("url") or ""))
            if normalized:
                normalized_counts[normalized] = normalized_counts.get(normalized, 0) + 1

        checked_items: list[dict[str, Any]] = []
        domains: set[str] = set()
        valid_url_count = 0
        for item in source_items:
            url = str(item.get("url") or "").strip()
            normalized = _normalize_url(url)
            item_domain = domain(url)
            checks: list[str] = []

            if not _is_valid_web_url(url):
                checks.append("invalid_url")
            else:
                valid_url_count += 1
                if item_domain:
                    domains.add(item_domain)
                if urlparse(url).scheme == "http":
                    checks.append("insecure_http")

            if normalized and normalized_counts.get(normalized, 0) > 1:
                checks.append("duplicate_url")
            if not str(item.get("source") or "").strip():
                checks.append("missing_source")
            if not checks:
                checks.append("ok")

            checked_items.append({
                "title": item.get("title") or "",
                "url": url,
                "domain": item_domain,
                "source": item.get("source") or "",
                "checks": checks,
            })

        duplicate_urls = sorted(url for url, count in normalized_counts.items() if count > 1)
        min_source_count = max(1, int(min_sources or 2))
        recommendation = "ok" if len(domains) >= min_source_count else "needs_more_independent_sources"

        warnings: list[str] = []
        if duplicate_urls:
            warnings.append("duplicate_urls_found")
        if any("invalid_url" in item["checks"] for item in checked_items):
            warnings.append("invalid_urls_found")
        if any("insecure_http" in item["checks"] for item in checked_items):
            warnings.append("insecure_http_found")
        if any("missing_source" in item["checks"] for item in checked_items):
            warnings.append("missing_source_labels_found")
        if recommendation != "ok":
            warnings.append("low_domain_diversity")

        return {
            "tool": "source_check",
            "item_count": len(source_items),
            "valid_url_count": valid_url_count,
            "unique_domain_count": len(domains),
            "duplicate_urls": duplicate_urls,
            "warnings": warnings,
            "recommendation": recommendation,
            "items": checked_items,
        }
    except Exception as exc:
        return err("source_check", exc)
