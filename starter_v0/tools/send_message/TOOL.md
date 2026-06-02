---
name: send_message
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
---
# send_message

Posts text to a Telegram channel. The message is only sent when `confirmed` is true.
