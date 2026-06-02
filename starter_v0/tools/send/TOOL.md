---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
---
# send

Post a message to a Telegram channel via the Bot API. **This is an action tool with side effects** — the message is only sent when `confirmed` is explicitly `true`. Always ask the user for confirmation before calling with `confirmed=true`.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | **yes** | `""` | The message text to send. Supports Telegram Markdown formatting. |
| `confirmed` | boolean | **yes** | `false` | Safety gate. Set to `true` only after the user explicitly confirms they want to send. |

## Return Format

When `confirmed=false` (default — no message sent):
```json
{
  "tool": "send_telegram",
  "status": "needs_confirmation",
  "message": "Only send after the user explicitly confirms."
}
```

When `confirmed=true` (message sent successfully):
```json
{
  "tool": "send_telegram",
  "status": "sent"
}
```

## Notes

- **CRITICAL**: Never set `confirmed=true` without explicit user approval. Use the `clarify` tool first to ask.
- Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables.
- Uses Telegram's `Markdown` parse mode.
- On error (missing env vars, network failure), returns `{"tool": "send_telegram", "error": "..."}`.
