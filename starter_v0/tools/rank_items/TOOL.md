---
name: rank_items
track: bonus
kind: local_sort
requires_env: []
inputs: [items, criteria, order, top_k]
outputs: [ranked, count, total]
side_effect: false
---
# rank_items

Sort and rank a list of items by a numeric field. Use this tool after collecting and deduplicating items to surface the most important ones (by engagement, relevance score, date, etc.) before formatting.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `items` | list[object] | **yes** | `[]` | List of item objects to rank. Each item should have the field specified by `criteria`, or a nested `metrics` dict containing it. |
| `criteria` | string | no | `"score"` | The numeric field to sort by (e.g. `"score"`, `"favorites"`, `"retweets"`, `"views"`). Also checks inside `item.metrics` if the top-level field is missing. |
| `order` | string | no | `"desc"` | Sort direction: `"desc"` (highest first) or `"asc"` (lowest first). |
| `top_k` | integer | no | `10` | Maximum number of items to return (1 to total items). |

## How Sorting Works

1. For each item, the tool reads the value at `item[criteria]`. If not found, it checks `item["metrics"][criteria]`.
2. Values are converted to numbers: plain numbers pass through; strings like `"1.5K"`, `"3.2M"` are expanded to numeric values.
3. Items are sorted and the top K are returned with an added `_rank` field (1-indexed).

## Return Format

```json
{
  "tool": "rank_items",
  "ranked": [
    {
      "title": "Most Popular Tweet",
      "summary": "Full tweet text...",
      "url": "https://x.com/user/status/123",
      "source": "@user",
      "metrics": {
        "favorites": 500,
        "retweets": 120,
        "views": 50000
      },
      "_rank": 1
    },
    {
      "title": "Second Most Popular",
      "metrics": { "favorites": 200, "retweets": 50, "views": 10000 },
      "_rank": 2
    }
  ],
  "criteria": "favorites",
  "order": "desc",
  "count": 2,
  "total": 15
}
```

On empty input:
```json
{
  "tool": "rank_items",
  "ranked": [],
  "criteria": "score",
  "order": "desc",
  "count": 0
}
```

## Notes

- **No API key required** — pure local computation.
- The `_rank` field is added **in-place** to the returned items (1-indexed).
- Supports human-readable number suffixes: `K` (thousands), `M` (millions), `B` (billions).
- If a value cannot be parsed as a number, it defaults to `0.0`.
- `top_k` is clamped to `[1, len(items)]` — you cannot request more items than you have.
- Common usage: rank tweets by `favorites` or `retweets`; rank search results by `score`; rank papers by date with `criteria="published"`.
