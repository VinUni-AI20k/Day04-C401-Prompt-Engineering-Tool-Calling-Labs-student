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

Extract structured entities from free text using regex patterns. Use this tool to pull out emails, URLs, arXiv IDs, hashtags, mentions, dates, and numbers from articles, tweets, or any text block. Helpful for follow-up actions like fetching URLs, looking up papers, or identifying contacts.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | **yes** | `""` | The text to extract entities from. |
| `entity_types` | list[string] \| null | no | `null` | Which entity types to extract. Omit or pass `null` to extract all types. See supported types below. |

### Supported Entity Types

| Type | Pattern | Examples |
|------|---------|---------|
| `emails` | Standard email pattern | `user@example.com` |
| `urls` | HTTP/HTTPS URLs | `https://arxiv.org/abs/2401.12345` |
| `arxiv_ids` | arXiv paper IDs (with optional version) | `2401.12345`, `2310.06775v2` |
| `hashtags` | Twitter/social hashtags | `#AI`, `#MachineLearning` |
| `mentions` | Twitter @-mentions | `@OpenAI`, `@elonmusk` |
| `dates` | Date strings in common formats | `2024-01-15`, `January 15, 2024` |
| `numbers` | Numeric values (integers, floats, with suffixes) | `42`, `3.14`, `1.5K`, `10M` |

## Return Format

```json
{
  "tool": "extract_entities",
  "entities": {
    "emails": ["contact@example.com"],
    "urls": ["https://arxiv.org/abs/2401.12345"],
    "arxiv_ids": ["2401.12345"],
    "hashtags": ["#AI", "#AGI"],
    "mentions": ["@OpenAI"],
    "dates": ["2024-01-15"],
    "numbers": ["42", "3.5K"]
  },
  "total_found": 8,
  "entity_types_searched": ["emails", "urls", "arxiv_ids", "hashtags", "mentions", "dates", "numbers"],
  "text_length": 1200
}
```

On empty input:
```json
{
  "tool": "extract_entities",
  "error": "empty_input",
  "message": "No text provided."
}
```

## Notes

- **No API key required** — pure local computation using regex patterns.
- All entity values are **deduplicated** within each type (same URL appearing twice returns once).
- The `numbers` type is capped at **20 results** to avoid noise from dense text.
- Only entity types actually found appear in the `entities` dict (empty types are omitted).
- `entity_types_searched` confirms which types were requested (intersection of your input and supported types).
- This tool does **not** extract named persons or organizations — for that, use an LLM-based approach.
