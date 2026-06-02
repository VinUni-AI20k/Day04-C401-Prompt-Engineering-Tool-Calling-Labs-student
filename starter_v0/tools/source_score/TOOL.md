---
name: source_score
track: bonus
kind: source_quality
provider: local
requires_env: []
inputs: [url, title, source]
outputs: [domain, score, rating, reasons, guidance]
side_effect: false
---
# source_score

Scores a source URL/domain with a simple local heuristic. Use it when the agent
needs a lightweight signal about source quality before citing or comparing items.
The score is guidance only and does not verify whether a claim is true.
