---
name: arxiv_search
track: bonus
kind: live_api
provider: arXiv API
requires_env: [ARXIV_USER_AGENT]
inputs: [query, max_results, sort_by]
outputs: [items, total_results]
side_effect: false
---
# arxiv_search

Bonus research tool. It searches arXiv via the official Atom API. arXiv is
rate-limited; the tool waits at least 3 seconds between in-process requests.

