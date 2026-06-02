---
name: summarize
track: new
kind: local_nlp
requires_env: []
inputs: [text, max_sentences, language]
outputs: [summary, sentence_count, original_length, summary_length]
side_effect: false
---
# summarize

Extract the most important sentences from a text block using extractive summarization. This is a local tool — no API calls, no env vars needed. Use it to condense long articles, paper abstracts, or scraped page content.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | **yes** | `""` | The text to summarize. |
| `max_sentences` | integer | no | `5` | Maximum number of sentences to keep in the summary (1+). |
| `language` | string | no | `"auto"` | Language hint (currently unused — handles both English and Vietnamese punctuation automatically). |

## Return Format

```json
{
  "tool": "summarize_text",
  "summary": "The most important sentences in original order...",
  "sentence_count": 3,
  "original_sentences": 15,
  "original_length": 2400,
  "summary_length": 480
}
```

On empty input:
```json
{
  "tool": "summarize_text",
  "error": "empty_input",
  "message": "No text provided to summarize."
}
```

## Notes

- **No API key required** — pure local computation using regex-based extractive summarization.
- Scoring uses: word frequency, sentence position (first/last boosted), and sentence length.
- Sentences shorter than 10 characters are filtered out.
- Output sentences are returned in their **original order** (not by score).
- Works with both English and Vietnamese text (splits on `.!?。`).
