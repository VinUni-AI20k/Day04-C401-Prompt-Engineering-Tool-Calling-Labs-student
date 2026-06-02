---
name: reddit
track: bonus
kind: live_api
provider: Apify
requires_env: [APIFY_API_KEY]
inputs: [query, max_results, sort, timeframe, content_type]
outputs: [items]
side_effect: false
---
# reddit

Search Reddit posts and comments using Apify's Reddit Search Scraper.
Returns posts with title, body text, score, subreddit, and URL.
