---
name: format
track: core
kind: local_formatter
requires_env: []
inputs: [items, template, headline]
outputs: [markdown, item_count]
side_effect: false
---
# format

Format a list of already-collected items into a readable markdown digest. This tool does **not** fetch any data — it only renders items you already have.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `items` | list[object] \| null | **yes** | `[]` | List of item objects. Each item should have `title`, `summary`, `url`, `source`, and optionally `section`. |
| `template` | string | no | `"sections"` | Layout template. One of: `"brief"`, `"bullets"`, `"thread"`, `"sections"`, `"daily_ai_vn"`. |
| `headline` | string | no | `""` | Optional headline/title displayed at the top of the digest. |

### Template Options

| Template | Description |
|----------|-------------|
| `brief` | Bold headline + up to 5 bullet items. |
| `bullets` | Simple bullet list of all items. |
| `thread` | Numbered thread format (1/, 2/, 3/…). |
| `sections` | Items grouped by `section` field with `## Section` headers. Default. |
| `daily_ai_vn` | Vietnamese daily news format, grouped by `section`. |

## Return Format

```json
{
  "tool": "render_digest",
  "template": "sections",
  "markdown": "# Headline\n\n## Section\n- Item summary - [source](url)\n",
  "item_count": 5
}
```

## Notes

- Each item's summary is truncated to 280 characters in the output.
- Items are rendered as `- {summary} - [{source}]({url})`.
- The `section` field on items controls grouping for `sections` and `daily_ai_vn` templates.
- If no `section` is set, items default to `"Tổng hợp"` (sections) or `"Tin chính"` (daily_ai_vn).
