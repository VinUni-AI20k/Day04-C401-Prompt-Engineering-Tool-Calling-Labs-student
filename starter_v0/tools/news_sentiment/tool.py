import os
import requests


def _simple_sentiment(text: str) -> str:
    """
    Very simple keyword-based sentiment classifier.
    This is not a machine learning model.
    It is only used to summarize the tone of retrieved news snippets.
    """
    text_lower = text.lower()

    negative_words = [
        "lawsuit", "risk", "ban", "decline", "loss", "harm",
        "unsafe", "concern", "investigation", "crisis", "warning",
        "threat", "controversy", "fraud", "attack", "fail"
    ]

    positive_words = [
        "growth", "profit", "launch", "improve", "success",
        "partnership", "funding", "innovation", "record",
        "expansion", "breakthrough", "raise", "gain"
    ]

    negative_score = sum(1 for word in negative_words if word in text_lower)
    positive_score = sum(1 for word in positive_words if word in text_lower)

    if positive_score > negative_score:
        return "positive"
    if negative_score > positive_score:
        return "negative"
    return "neutral"


def run(topic: str, timeframe: str = "week", max_results: int = 5) -> dict:
    """
    Search recent news using Tavily API and return a lightweight sentiment/risk scan.

    Args:
        topic: Topic to analyze.
        timeframe: day, week, month, or year.
        max_results: Number of search results.

    Returns:
        Dictionary with sentiment summary and source items.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "ok": False,
            "error": "Missing TAVILY_API_KEY environment variable.",
        }

    if not topic or not topic.strip():
        return {
            "ok": False,
            "error": "Missing required argument: topic.",
        }

    topic = topic.strip()

    # Tavily supports topic=news in many setups.
    # days is approximate because the existing lookup tool also uses abstract timeframe.
    days_map = {
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
    }

    days = days_map.get(timeframe, 7)

    payload = {
        "query": topic,
        "topic": "news",
        "search_depth": "basic",
        "max_results": max_results,
        "days": days,
        "include_answer": False,
        "include_raw_content": False,
    }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )

        response.raise_for_status()
        data = response.json()

    except Exception as exc:
        return {
            "ok": False,
            "error": "Tavily API request failed.",
            "message": str(exc),
        }

    results = data.get("results", [])

    items = []

    sentiment_counts = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }

    for result in results:
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "") or result.get("snippet", "")

        combined_text = f"{title}\n{content}"
        sentiment = _simple_sentiment(combined_text)

        sentiment_counts[sentiment] += 1

        items.append(
            {
                "title": title,
                "url": url,
                "summary": content,
                "sentiment": sentiment,
                "source": result.get("source", ""),
            }
        )

    if sentiment_counts["negative"] >= max(2, sentiment_counts["positive"] + 1):
        overall_sentiment = "negative"
        risk_level = "high"
    elif sentiment_counts["positive"] > sentiment_counts["negative"]:
        overall_sentiment = "positive"
        risk_level = "low"
    else:
        overall_sentiment = "mixed"
        risk_level = "medium"

    return {
        "ok": True,
        "tool": "news_sentiment",
        "topic": topic,
        "timeframe": timeframe,
        "overall_sentiment": overall_sentiment,
        "risk_level": risk_level,
        "sentiment_counts": sentiment_counts,
        "items": items,
    }