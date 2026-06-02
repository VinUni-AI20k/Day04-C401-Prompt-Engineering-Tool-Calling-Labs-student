---
name: ask_user
track: core
kind: control
requires_env: []
inputs: [question, response_type, options]
outputs: [question, response_type, options, awaiting_user]
side_effect: false
---
# ask_user

Use when a required argument is missing or a write action needs confirmation.
The chat loop renders the returned question and waits for the next user turn.

