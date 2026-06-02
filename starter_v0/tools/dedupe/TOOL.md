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

Removes near-duplicate items from a list using Jaccard word-set similarity.
Compare items on a chosen field (default: `summary`). Items with similarity
≥ threshold (default 0.6) are considered duplicates; only the first is kept.
Runs locally, no API needed.
