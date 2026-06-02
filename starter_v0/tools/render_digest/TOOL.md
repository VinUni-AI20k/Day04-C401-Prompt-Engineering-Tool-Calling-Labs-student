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

Formats already-collected items into a markdown digest. It does not fetch data.
