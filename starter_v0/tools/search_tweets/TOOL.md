---
name: search_tweets
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [query, search_type, limit]
outputs: [items]
side_effect: false
---
# search_tweets

Use for tweets about a topic. Do not use it for tweets from a specific account.

