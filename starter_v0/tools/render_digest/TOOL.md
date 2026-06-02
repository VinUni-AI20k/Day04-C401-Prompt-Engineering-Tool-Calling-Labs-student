---
name: render_digest
track: core
kind: local_formatter
requires_env: []
inputs: [items, template, headline]
outputs: [markdown, item_count]
side_effect: false
---
# render_digest

Use after research tools have returned items. It formats existing data only; it
does not fetch new evidence and does not summarize missing content.

