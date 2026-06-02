from __future__ import annotations

from typing import Any

from tools._shared import err, terms


TIMEFRAME_MAP = {
    "hôm nay": "day",
    "today": "day",
    "tuần này": "week",
    "this week": "week",
    "tháng này": "month",
    "this month": "month",
    "năm nay": "year",
    "this year": "year",
}


def make_query_plan(topic: str = "", goal: str = "overview", language: str = "vi") -> dict[str, Any]:
    try:
        clean_topic = " ".join(topic.split()).strip()
        clean_goal = " ".join((goal or "overview").split()).strip().lower()
        folded = f"{clean_topic} {clean_goal}".lower()
        timeframe = None
        for marker, value in TIMEFRAME_MAP.items():
            if marker in folded:
                timeframe = value
                break

        topic_terms = sorted(terms(clean_topic))
        base_query = clean_topic
        if clean_goal in {"news", "tin", "tin tức", "latest"} and topic_terms:
            base_query = " ".join(topic_terms)

        searches = [
            {"query": base_query or clean_topic, "purpose": "broad_overview"},
            {"query": f"{base_query} source official".strip(), "purpose": "primary_or_official_source"},
            {"query": f"{base_query} analysis".strip(), "purpose": "context_and_analysis"},
        ]

        return {
            "tool": "make_query_plan",
            "topic": clean_topic,
            "goal": clean_goal,
            "language": language,
            "timeframe": timeframe,
            "searches": searches,
            "suggested_tools": ["lookup"],
            "guidance": "Run the broad query first, then use official-source and analysis queries if the answer needs more confidence.",
        }
    except Exception as exc:
        return err("make_query_plan", exc)
