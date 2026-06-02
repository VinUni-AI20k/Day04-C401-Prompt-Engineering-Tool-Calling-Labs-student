---
name: rss
track: bonus
kind: live_api
provider: null
requires_env: []
inputs: [url, max_items]
outputs: [feed_title, items]
side_effect: false
---
# rss

Fetches and parses an RSS/Atom feed from a given URL.
Returns feed metadata and the latest items with title, link, summary, and published date.

Useful for monitoring specific blogs, news sites, or podcasts that provide RSS feeds.
