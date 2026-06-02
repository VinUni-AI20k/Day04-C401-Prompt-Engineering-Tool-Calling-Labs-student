---
name: get_user_timeline
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [screenname, limit]
outputs: [items]
side_effect: false
---
# get_user_timeline

Fetches recent posts from a single account. `screenname` is an account handle
without `@`.
