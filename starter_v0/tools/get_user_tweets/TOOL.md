---
name: get_user_tweets
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [screenname, limit]
outputs: [items]
side_effect: false
---
# get_user_tweets

Use for tweets from one known account. The input `screenname` is the handle
without `@`, for example `sama`, `elonmusk`, or `karpathy`.

