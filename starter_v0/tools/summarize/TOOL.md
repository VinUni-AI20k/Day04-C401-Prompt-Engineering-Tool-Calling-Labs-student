---
name: summarize
track: bonus
kind: local_nlp
requires_env: []
inputs: [text, max_sentences, language]
outputs: [summary, sentence_count, original_length, summary_length]
side_effect: false
---
# summarize

Extractive summarization: scores sentences by keyword frequency and position,
then returns the top N sentences in original order. Works for both English and
Vietnamese text. No external API needed — runs entirely locally.
