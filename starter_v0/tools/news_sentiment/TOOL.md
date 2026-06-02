---
name: news_sentiment
track: custom
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [topic, timeframe, max_results]
outputs: [overall_sentiment, risk_level, sentiment_counts, items]
side_effect: false
requires_confirmation: false
---

# news_sentiment

Searches recent news about a topic using Tavily API and returns a lightweight sentiment/risk scan.

Use this tool when the user explicitly asks to analyze the tone, sentiment, risk level, or public signal in recent news about a topic.

This tool does not send, publish, or modify external systems.