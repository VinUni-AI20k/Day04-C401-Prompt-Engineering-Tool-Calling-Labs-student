---
name: dedupe
track: bonus
kind: local_nlp
requires_env: []
inputs: [items, key, threshold]
outputs: [unique, removed_count, unique_count]
side_effect: false
---
# dedupe

Remove near-duplicate items from a list using Jaccard word-set similarity. Use this tool after collecting items from multiple sources (search, social, papers) to filter out redundant or overlapping entries before formatting or ranking.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `items` | list[object] | **yes** | `[]` | List of item objects to deduplicate. Each item should have at least a `summary` or `title` field. |
| `key` | string | no | `"summary"` | The item field to compare for similarity (e.g. `"summary"`, `"title"`). Falls back to `"title"` if the key is missing on an item. |
| `threshold` | float | no | `0.6` | Similarity threshold (0.1–1.0). Items with Jaccard word-set similarity ≥ this value are considered duplicates. Lower = more aggressive dedup, higher = more lenient. |

## How Similarity Works

1. Both texts are **normalized**: lowercased, punctuation stripped, whitespace collapsed.
2. Each text is converted to a **word set**.
3. Similarity = `|intersection| / |union|` (Jaccard index).

For example, `"AI agents are transforming work"` vs `"AI agents transform the workplace"` share words `{ai, agents}` out of `{ai, agents, are, transforming, work, transform, the, workplace}` → similarity = 2/8 = 0.25.

## Return Format

```json
{
  "tool": "dedupe_items",
  "unique": [
    {
      "title": "Unique Item Title",
      "summary": "This item was kept because it is sufficiently different...",
      "url": "https://example.com/article1"
    }
  ],
  "removed_count": 3,
  "original_count": 8,
  "unique_count": 5,
  "threshold": 0.6,
  "key": "summary"
}
```

On empty input:
```json
{
  "tool": "dedupe_items",
  "unique": [],
  "removed_count": 0,
  "original_count": 0
}
```

## Notes

- **No API key required** — pure local computation.
- The threshold is clamped to [0.1, 1.0] to prevent extreme settings.
- Items with empty comparison text are always kept (never treated as duplicates).
- When multiple items are near-duplicates, the **first occurrence** is kept and later ones are removed.
- Use `key="title"` for tweet/social items where `summary` may vary but `title` is more stable.
