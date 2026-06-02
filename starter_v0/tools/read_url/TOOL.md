---
name: read_url
track: core
kind: live_api
provider: Firecrawl
requires_env: [FIRECRAWL_API_KEY]
inputs: [url]
outputs: [items]
side_effect: false
---
# read_url

Reads the content of a single URL via Firecrawl.
