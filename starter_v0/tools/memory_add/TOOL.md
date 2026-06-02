---
name: memory_add
track: bonus
kind: local_memory
provider: local_json
requires_env: []
inputs: [name, content, memory_type, tags]
outputs: [status, path, record]
side_effect: true
---
# memory_add

Stores a local lab memory record in `starter_v0/memory_store/*.json`.
Use only when the user explicitly asks to remember/save something for this lab
agent. This is local project memory, not the Claude Code persistent memory system.
