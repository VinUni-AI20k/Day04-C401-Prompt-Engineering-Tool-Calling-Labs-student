---
name: search_papers
track: bonus
kind: live_api
provider: arXiv API
requires_env: [ARXIV_USER_AGENT]
inputs: [query, max_results, sort_by]
outputs: [items, total_results]
side_effect: false
---
# search_papers

Searches arXiv via the official Atom API. Rate-limited (waits ~3s between
in-process requests).
