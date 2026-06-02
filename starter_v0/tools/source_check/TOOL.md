---
name: source_check
track: team
kind: local_formatter
provider: local
requires_env: []
inputs: [items, min_sources]
outputs: [items, duplicate_urls, unique_domain_count, recommendation]
side_effect: false
---
# source_check

Checks a list of research items for basic source hygiene before a digest or
report is sent. It detects duplicate URLs, insecure HTTP links, missing source
labels, invalid URLs, and whether the result set has enough independent source
domains.
