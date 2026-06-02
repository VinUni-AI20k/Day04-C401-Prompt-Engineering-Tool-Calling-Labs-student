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

Sorts a list of items by a numeric field (e.g. `score`, `favorites`, `views`,
`retweets`). Supports nested fields inside `metrics`. Returns the top K items
with a `_rank` field added. Use `order=asc` for ascending, default is descending.
