---
name: summarize
track: bonus
kind: local_formatter
provider: null
requires_env: []
inputs: [text, max_sentences]
outputs: [summary, original_length, summary_length]
side_effect: false
---
# summarize

Extractive summarization tool that picks the most important sentences from text.
Uses sentence scoring based on word frequency and position.
