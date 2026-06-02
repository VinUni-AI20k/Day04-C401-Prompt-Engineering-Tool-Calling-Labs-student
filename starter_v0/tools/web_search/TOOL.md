---
name: web_search
track: core
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [query, topic, timeframe, max_results]
outputs: [items]
side_effect: false
---
# web_search

Use for web/news search. For recent news, set `topic` to `news` and map
phrases like "today" or "hôm nay" to `timeframe=day`.

