---
name: lookup
track: core
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [query, topic, timeframe, max_results]
outputs: [items]
side_effect: false
---
# lookup

Search the web for real-time information using the Tavily search API. Use this tool when the user asks about current events, recent news, factual questions, or anything that requires up-to-date web data.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | **yes** | `""` | The search query string. Be specific for better results. |
| `topic` | string | no | `"general"` | Search category — `"general"` for broad web search, `"news"` for recent news articles only. |
| `timeframe` | string \| null | no | `"week"` | Time range filter. Accepted values: `"day"`, `"week"`, `"month"`, `"year"`, or `null` for no time restriction. |
| `max_results` | integer | no | `5` | Number of results to return (1–10). |

## Return Format

```json
{
  "tool": "web_search",
  "query": "...",
  "topic": "general",
  "timeframe": "week",
  "items": [
    {
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "example.com",
      "summary": "Brief content snippet from the page...",
      "score": 0.95
    }
  ]
}
```

## Notes

- Requires `TAVILY_API_KEY` environment variable to be set.
- Uses `search_depth: "basic"` for fast responses.
- Each item includes a relevance `score` (0–1); higher is more relevant.
- The `source` field is the domain extracted from the URL for easy attribution.
- On error (missing API key, network failure), returns `{"tool": "web_search", "error": "..."}`.
