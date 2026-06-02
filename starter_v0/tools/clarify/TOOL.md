---
name: clarify
track: core
kind: control
requires_env: []
inputs: [question, response_type, options]
outputs: [question, response_type, options, awaiting_user]
side_effect: false
---
# clarify

Pause the agent loop and ask the user a clarifying question. Use this tool when the user's request is ambiguous, missing key details, or when you need confirmation before proceeding.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | string | **yes** | `""` | The question to present to the user. |
| `response_type` | string | no | `"text"` | Expected answer format: `"text"` (free-form), `"yes_no"`, or `"choice"`. |
| `options` | list[string] \| null | no | `null` | List of choices when `response_type` is `"choice"`. Ignored otherwise. |

## Return Format

```json
{
  "tool": "ask_user",
  "question": "Which topic do you want?",
  "response_type": "choice",
  "options": ["AI", "Climate", "Finance"],
  "awaiting_user": true
}
```

## Notes

- This is a **control tool** — it does not call any external API.
- When `awaiting_user` is `true`, the agent loop should stop and wait for the next user message.
- Always prefer asking a focused, single question rather than multiple questions at once.
