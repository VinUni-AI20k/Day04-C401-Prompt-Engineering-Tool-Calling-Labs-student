from __future__ import annotations

from typing import Any

from tools._shared import terms


def rank_items(
    items: list[dict[str, Any]] | None = None,
    query: str = "",
    top_k: int = 5,
) -> dict[str, Any]:
    if not items:
        return {"tool": "rank_items", "error": "ValueError", "message": "items list is required"}
    if not query.strip():
        return {"tool": "rank_items", "ranked": items[:top_k], "scores": []}

    query_terms = terms(query)

    def score(item: dict[str, Any]) -> int:
        blob = " ".join(str(v) for v in item.values() if isinstance(v, str))
        return len(query_terms & terms(blob))

    ranked = sorted(items, key=score, reverse=True)
    scores = [score(item) for item in ranked]
    return {
        "tool": "rank_items",
        "query": query,
        "ranked": ranked[:top_k],
        "scores": scores[:top_k],
    }
