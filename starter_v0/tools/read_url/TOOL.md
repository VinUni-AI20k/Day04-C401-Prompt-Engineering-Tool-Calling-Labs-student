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

Use when the user gives a specific URL. If the user gives multiple URLs, call
this tool once per URL in the same model response.

