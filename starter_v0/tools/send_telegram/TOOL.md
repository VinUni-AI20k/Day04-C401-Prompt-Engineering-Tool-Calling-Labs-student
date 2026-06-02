---
name: send_telegram
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# send_telegram

Bonus action tool. It posts to a Telegram channel. The agent must call
`ask_user` for confirmation before calling this tool with `confirmed=true`.

