---
name: extract_entities
track: bonus
kind: local_nlp
requires_env: []
inputs: [text, entity_types]
outputs: [entities, total_found, entity_types_searched]
side_effect: false
---
# extract_entities

Extracts structured entities from free text using regex patterns. Supported
entity types: `emails`, `urls`, `arxiv_ids`, `hashtags`, `mentions`, `dates`,
`numbers`. Pass `entity_types` to filter; omit to extract all types.
Runs locally, no API needed.
