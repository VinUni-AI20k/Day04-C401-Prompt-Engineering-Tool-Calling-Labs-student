---
name: timeline
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [screenname, limit]
outputs: [items]
side_effect: false
---
# timeline

Fetch recent tweets from a specific Twitter/X account. Use this when the user wants to see what a particular person or organization has been posting.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `screenname` | string | **yes** | `""` | The Twitter handle **without** the `@` prefix (e.g. `"elonmusk"`, `"OpenAI"`). |
| `limit` | integer | no | `5` | Maximum number of tweets to return. |

## Return Format

```json
{
  "tool": "get_user_tweets",
  "screenname": "OpenAI",
  "items": [
    {
      "title": "First line of tweet (max 120 chars)",
      "summary": "Full tweet text",
      "url": "https://x.com/OpenAI/status/123456",
      "source": "@OpenAI",
      "date": "2026-06-01T12:00:00Z",
      "metrics": {
        "favorites": 100,
        "retweets": 25,
        "views": 50000
      }
    }
  ]
}
```

## Notes

- Requires `RAPIDAPI_KEY` and optionally `RAPIDAPI_TWITTER_HOST` (defaults to `twitter-api45.p.rapidapi.com`).
- Do **not** include `@` in the `screenname` parameter.
- Each item includes engagement `metrics` (favorites, retweets, views).
- On error, returns `{"tool": "get_user_tweets", "error": "..."}`.
