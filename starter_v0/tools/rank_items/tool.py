from __future__ import annotations


import re
from typing import Any


def _extract_number(value: Any) -> float:
    """Try to extract a numeric value from various formats."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Handle "1.2K", "3.5M" etc.
        match = re.match(r'^([\d.]+)\s*([KkMmBb]?)$', value.strip())
        if match:
            num = float(match.group(1))
            suffix = match.group(2).upper()
            multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
            return num * multipliers.get(suffix, 1)
        # Try plain float
        try:
            return float(value)
        except ValueError:
            pass
    return 0.0

from typing import Any


def rank_items(
    items: list[dict[str, Any]] | None = None,
    criteria: str = "score",
    order: str = "desc",
    top_k: int = 10,
) -> dict[str, Any]:
    """Sort and rank a list of items by a numeric field or nested metric."""
    items = items or []
    if not items:
        return {"tool": "rank_items", "ranked": [], "criteria": criteria, "order": order, "count": 0}

    top_k = max(1, min(int(top_k or 10), len(items)))

    def get_sort_value(item: dict[str, Any]) -> float:
        # Direct field
        if criteria in item:
            return _extract_number(item[criteria])
        # Check nested in "metrics" dict (common for tweet items)
        metrics = item.get("metrics", {})
        if isinstance(metrics, dict) and criteria in metrics:
            return _extract_number(metrics[criteria])
        return 0.0

    reverse = order.lower() != "asc"
    sorted_items = sorted(items, key=get_sort_value, reverse=reverse)
    ranked = sorted_items[:top_k]

    # Add rank field
    for idx, item in enumerate(ranked):
        item["_rank"] = idx + 1

    return {
        "tool": "rank_items",
        "ranked": ranked,
        "criteria": criteria,
        "order": "desc" if reverse else "asc",
        "count": len(ranked),
        "total": len(items),
    }
