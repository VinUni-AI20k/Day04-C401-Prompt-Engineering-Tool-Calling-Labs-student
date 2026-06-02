---
name: social_search
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [query, search_type, limit]
outputs: [items]
side_effect: false
---
# social_search

Search Twitter/X posts by keyword using the RapidAPI Twitter API45. Use this to find social media discussions, opinions, or trending topics.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | **yes** | `""` | The search query (keywords, hashtags, etc.). |
| `search_type` | string | no | `"Latest"` | Result ordering: `"Latest"` (most recent first) or `"Top"` (most popular first). |
| `limit` | integer | no | `5` | Maximum number of tweets to return. |

## Return Format

```json
{
  "tool": "search_tweets",
  "query": "AI agents",
  "search_type": "Latest",
  "items": [
    {
      "title": "First line of tweet (max 120 chars)",
      "summary": "Full tweet text",
      "url": "https://x.com/handle/status/123456",
      "source": "@handle",
      "date": "2026-06-01T12:00:00Z",
      "metrics": {
        "favorites": 42,
        "retweets": 10,
        "views": 5000
      }
    }
  ]
}
```

## Notes

- Requires `RAPIDAPI_KEY` and optionally `RAPIDAPI_TWITTER_HOST` (defaults to `twitter-api45.p.rapidapi.com`).
- Each item includes engagement `metrics` (favorites, retweets, views).
- The `title` field is the first line of the tweet, truncated to 120 characters.
- On error, returns `{"tool": "search_tweets", "error": "..."}`.
