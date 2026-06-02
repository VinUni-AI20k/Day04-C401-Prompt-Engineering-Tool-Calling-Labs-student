---
name: sentiment
track: bonus
kind: local_knowledge
provider: null
requires_env: []
inputs: [text]
outputs: [sentiment, score, positive_words, negative_words]
side_effect: false
---
# sentiment

Basic sentiment analysis using word lists.
Returns sentiment (positive/negative/neutral), confidence score, and matched words.
Works for English and basic Vietnamese.
